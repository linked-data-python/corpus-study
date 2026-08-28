"""Scaffold LD Python counterparts for the extracted regions.

For every region this stage materialises an example directory

    examples/<band>/<region_id>/
        original.py       provenance header + context + region source
        translated.ldpy   MECHANICAL DRAFT of the LD Python counterpart
        driver.py         validation driver scaffold (see rdfeval.harness)
        meta.json         provenance + translation status/classification

The mechanical assistant (:func:`draft_translation`) performs only
semantics-preserving rewrites:

  * ``NS = Namespace("<iri>")`` and well-known ``rdflib.namespace`` imports
    become ``@prefix`` declarations;
  * ``NS.term`` / ``NS["term"]`` become prefixed names;
  * ``URIRef("<constant>")`` becomes an IRI island;
  * ``Literal(c, lang=...)`` / ``Literal(c, datatype=XSD.x)`` become RDF
    literal islands;
  * consecutive ``g.add((s, p, o))`` statements over one graph become a
    single ``g += g{ ... }`` island, with non-island term expressions kept
    as ``{expr}`` interpolations.

Everything else is left untouched.  The draft is exactly that — a draft:
``meta.json`` starts with ``"translation_status": "draft"`` and the pair
enters validation/comparison only once a human review has set it to
``"final"`` and filled ``"classification"`` with one of:

    directly-expressible | minor-restructuring | awkward | not-expressible
    | excluded

Re-running the stage NEVER overwrites an example whose status is not
``draft`` (and keeps drafts whose files were hand-edited, detected by
content hash).
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import textwrap

from .config import EXAMPLES_DIR, provenance
from .regions import load_regions

PN_LOCAL_OK = re.compile(r"[A-Za-z_][\w.-]*$")   # conservative subset


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


# --- well-known namespace IRIs (resolved from the installed rdflib) ---------

def well_known_iris() -> dict[str, str]:
    import rdflib.namespace as ns
    out = {}
    for name in dir(ns):
        if name.isupper():
            obj = getattr(ns, name)
            iri = None
            if isinstance(obj, ns.Namespace):
                iri = str(obj)
            else:
                iri = str(getattr(obj, "_NS", "") or "")
            if iri.startswith("http"):
                out[name] = iri
    return out


# --- the mechanical assistant ----------------------------------------------

RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"


class Draft:
    def __init__(self, source: str):
        self.source = source
        self.lines = source.splitlines()
        self.notes: list[str] = []
        # var -> (prefix label, namespace IRI, bare_usable)
        self.prefixes: dict[str, tuple[str, str, bool]] = {}
        # names bound to rdf:type (the `A = RDF.type` idiom)
        self.type_aliases: set[str] = set()
        # var -> blank-node label, for BNode("label") bound to a variable
        self.bnode_labels: dict[str, str] = {}

    def add_note(self, msg: str) -> None:
        if msg not in self.notes:
            self.notes.append(msg)


def _term_to_island(node: ast.expr, d: Draft, src: str) -> str | None:
    """Island syntax for a term expression, or None to interpolate."""
    if isinstance(node, ast.Call):
        fn = node.func
        name = fn.id if isinstance(fn, ast.Name) else (
            fn.attr if isinstance(fn, ast.Attribute) else None)
        if name == "URIRef" and len(node.args) == 1 and not node.keywords:
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str) \
                    and "<" not in arg.value and ">" not in arg.value \
                    and " " not in arg.value:
                return f"<{arg.value}>"
        if name == "Literal" and node.args:
            arg = node.args[0]
            kws = {k.arg: k.value for k in node.keywords}
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                s = json.dumps(arg.value)
                if set(kws) == {"lang"} and isinstance(kws["lang"], ast.Constant):
                    return f'{s}@{kws["lang"].value}'
                if set(kws) == {"datatype"}:
                    dt = _term_to_island(kws["datatype"], d, src)
                    if dt and not dt.startswith("{"):
                        return f"{s}^^{dt}"
                if not kws:
                    return s          # plain string literal object
            if isinstance(arg, ast.Constant) and isinstance(arg.value, (int, float, bool)) \
                    and not kws:
                return repr(arg.value)
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        pref = d.prefixes.get(node.value.id)
        if pref and PN_LOCAL_OK.match(node.attr):
            if pref[1] == RDF_NS and node.attr == "type":
                return "a"
            return f"{pref[0]}:{node.attr}"
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
        pref = d.prefixes.get(node.value.id)
        sl = node.slice
        if pref:
            if isinstance(sl, ast.Constant) and isinstance(sl.value, str) \
                    and PN_LOCAL_OK.match(sl.value):
                return f"{pref[0]}:{sl.value}"
            # ex:{expr} — prefixed name with an interpolated local part
            if not isinstance(sl, ast.Slice):
                return f"{pref[0]}:{{{_expr_src(sl, src)}}}"
    if isinstance(node, ast.Name):
        # a name bound to rdf:type (the `A = RDF.type` idiom) is Turtle's `a`
        if node.id in d.type_aliases:
            return "a"
        pref = d.prefixes.get(node.id)
        if pref and pref[2]:            # a bare namespace used as a term
            return f"<{pref[1]}>"
        if node.id in d.bnode_labels:
            return f"_:{d.bnode_labels[node.id]}"
    if isinstance(node, ast.Constant) and isinstance(node.value, (str, int, float)):
        return json.dumps(node.value) if isinstance(node.value, str) else repr(node.value)
    return None


def _expr_src(node: ast.expr, src: str) -> str:
    return ast.get_source_segment(src, node) or ast.unparse(node)


def _term(node: ast.expr, d: Draft, src: str) -> str:
    island = _term_to_island(node, d, src)
    if island is not None:
        return island
    return "{" + _expr_src(node, src) + "}"


def _namespace_bindings(tree: ast.Module) -> tuple[dict[str, str], set[str]]:
    """Module-level ``X = Namespace("iri")`` bindings and rdf:type aliases."""
    ns: dict[str, str] = {}
    type_aliases: set[str] = set()
    for stmt in ast.walk(tree):
        if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1:
            continue
        target = stmt.targets[0]
        if not isinstance(target, ast.Name):
            continue
        val = stmt.value
        if isinstance(val, ast.Call):
            fn = val.func
            name = fn.id if isinstance(fn, ast.Name) else (
                fn.attr if isinstance(fn, ast.Attribute) else None)
            if name in ("Namespace", "ClosedNamespace") and val.args \
                    and isinstance(val.args[0], ast.Constant) \
                    and isinstance(val.args[0].value, str):
                ns[target.id] = val.args[0].value
        elif isinstance(val, ast.Attribute) and val.attr == "type" \
                and isinstance(val.value, ast.Name) and val.value.id == "RDF":
            type_aliases.add(target.id)
    return ns, type_aliases


# Suffixes a project adds to a namespace constant's name and that carry no
# meaning in a prefix label: `OWL_NS = Namespace(...)` is the OWL namespace.
_NOISE_SUFFIXES = ("NS", "NAMESPACE", "URI", "IRI", "PREFIX")


def _label_for(var: str, taken: set[str]) -> str | None:
    """Prefix label for a namespace constant named ``var``.

    The label must be usable **everywhere**, islands and Python code alike,
    so it is restricted to the intersection of Python identifiers and
    Turtle's ``PN_PREFIX``: a hyphen stays subtraction outside an island
    (reference/language/lexical.md), so ``OWL_NS`` may not become ``owl-ns``.
    Underscores are dropped, and a trailing noise segment with them.
    """
    parts = [p for p in var.split("_") if p]
    while len(parts) > 1 and parts[-1].upper() in _NOISE_SUFFIXES:
        parts.pop()
    label = "".join(parts).lower()
    if not re.match(r"[a-z][a-z0-9]*$", label) or label in taken:
        return None
    return label


def _after_last_toplevel_import(lines: list[str]) -> int:
    """Index just past the last module-level import statement.

    Bracket depth is tracked so a parenthesised list — ``from rdflib import
    (\n    Graph,\n)`` — is treated as the single statement it is: inserting
    a declaration between its lines would not parse.  Indented imports are
    ignored: a ``@prefix`` is block-scoped, so it never moves inside a body.
    """
    insert_at = 0
    depth = 0
    in_import = False
    continued = False
    for i, line in enumerate(lines):
        text = line or ""
        if depth == 0 and not continued:
            in_import = bool(re.match(r"(import|from)\s", text))
        stripped = re.sub(r"(?<!\\)#.*$", "", text)
        depth += (stripped.count("(") + stripped.count("[") + stripped.count("{")
                  - stripped.count(")") - stripped.count("]")
                  - stripped.count("}"))
        depth = max(depth, 0)
        continued = stripped.rstrip().endswith("\\")
        if in_import and depth == 0 and not continued:
            insert_at = i + 1
            in_import = False
    return insert_at


def draft_translation(source: str, resolve_module=None) -> tuple[str, list[str]]:
    """Best-effort mechanical rewrite of an rdflib module into ldpy.

    ``resolve_module(module, level)`` optionally returns the source of an
    imported module, so namespaces defined in a project's own
    ``namespaces.py`` (``from .namespaces import BRICK, SH``) become
    ``@prefix`` declarations instead of interpolations.
    """
    d = Draft(source)
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return source, [f"unparsable: {e}"]

    wk = well_known_iris()
    used = set(re.findall(r"[A-Za-z_][\w]*", source))
    prefix_decls: list[str] = []
    drop_stmts: list[ast.stmt] = []
    taken: set[str] = set()

    def declare(var: str, iri: str, bare_usable: bool = False) -> bool:
        if var in d.prefixes:
            return False
        label = _label_for(var, taken)
        if label is None:
            return False
        d.prefixes[var] = (label, iri, bare_usable)
        taken.add(label)
        decl = f"@prefix {label}: <{iri}> ."
        if decl not in prefix_decls:
            prefix_decls.append(decl)
        return True

    # 1. namespaces defined in this very source
    local_ns, local_type_aliases = _namespace_bindings(tree)
    d.type_aliases |= local_type_aliases
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 \
                and isinstance(stmt.targets[0], ast.Name) \
                and stmt.targets[0].id in local_ns:
            var = stmt.targets[0].id
            if declare(var, local_ns[var]):
                drop_stmts.append(stmt)

    # 2. namespaces imported from rdflib (well-known) or from project modules
    for stmt in ast.walk(tree):
        if not isinstance(stmt, ast.ImportFrom):
            continue
        module = stmt.module or ""
        if module.startswith("rdflib"):
            for alias in stmt.names:
                var = alias.asname or alias.name
                if alias.name in wk and var in used:
                    declare(var, wk[alias.name])
            continue
        if resolve_module is None:
            continue
        imported_src = resolve_module(module, stmt.level)
        if not imported_src:
            continue
        try:
            imported_tree = ast.parse(imported_src)
        except SyntaxError:
            continue
        ext_ns, ext_type_aliases = _namespace_bindings(imported_tree)
        for alias in stmt.names:
            var = alias.asname or alias.name
            if alias.name in ext_type_aliases:
                d.type_aliases.add(var)
            elif alias.name in ext_ns and var in used:
                declare(var, ext_ns[alias.name])

    # 3. BNode("label") variables -> _:label
    for stmt in ast.walk(tree):
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 \
                and isinstance(stmt.targets[0], ast.Name) \
                and isinstance(stmt.value, ast.Call):
            fn = stmt.value.func
            name = fn.id if isinstance(fn, ast.Name) else (
                fn.attr if isinstance(fn, ast.Attribute) else None)
            if name == "BNode" and len(stmt.value.args) == 1 \
                    and isinstance(stmt.value.args[0], ast.Constant) \
                    and isinstance(stmt.value.args[0].value, str) \
                    and re.match(r"[A-Za-z_][\w-]*$", stmt.value.args[0].value):
                d.bnode_labels[stmt.targets[0].id] = stmt.value.args[0].value

    # collect rewrites over statements (module + function bodies)
    edits: list[tuple[int, int, str]] = []   # (start_line0, end_line0, text)
    src = source

    def stmt_indent(stmt: ast.stmt) -> str:
        line = d.lines[stmt.lineno - 1]
        return line[:len(line) - len(line.lstrip())]

    def is_add_call(stmt: ast.stmt):
        if (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)
                and isinstance(stmt.value.func, ast.Attribute)
                and stmt.value.func.attr == "add"
                and len(stmt.value.args) == 1
                and isinstance(stmt.value.args[0], ast.Tuple)
                and len(stmt.value.args[0].elts) == 3):
            recv = stmt.value.func.value
            return _expr_src(recv, src)
        return None

    def process_body(body: list[ast.stmt], collect_only: bool = False) -> None:
        i = 0
        while i < len(body):
            recv = is_add_call(body[i])
            if recv is None:
                i += 1
                continue
            j = i
            run = []
            while j < len(body) and is_add_call(body[j]) == recv:
                run.append(body[j])
                j += 1
            if collect_only:
                run_spans.append((run[0].lineno, run[-1].end_lineno))
                i = j
                continue
            if len(run) >= 1:
                triples = []
                for stmt in run:
                    s, p, o = stmt.value.args[0].elts
                    triples.append((_term(s, d, src), _term(p, d, src),
                                    _term(o, d, src)))
                indent = stmt_indent(run[0])
                # group consecutive same-subject triples with ';'
                parts: list[str] = []
                k = 0
                while k < len(triples):
                    s0 = triples[k][0]
                    grouped = [f"{triples[k][1]} {triples[k][2]}"]
                    k += 1
                    while k < len(triples) and triples[k][0] == s0:
                        grouped.append(f"{triples[k][1]} {triples[k][2]}")
                        k += 1
                    parts.append(s0 + " " + (" ;\n" + indent + "       ").join(grouped))
                body_txt = (" .\n" + indent + "    ").join(parts)
                if len(run) == 1 and len(parts) == 1 and "\n" not in body_txt:
                    text = f"{indent}{recv} += g{{ {body_txt} }}"
                else:
                    text = (f"{indent}{recv} += g{{\n{indent}    {body_txt}\n"
                            f"{indent}}}")
                edits.append((run[0].lineno - 1, run[-1].end_lineno - 1, text))
            i = j

        # recurse into compound statements
        for stmt in body:
            for attr in ("body", "orelse", "finalbody"):
                sub = getattr(stmt, attr, None)
                if sub:
                    process_body(sub, collect_only)
            for handler in getattr(stmt, "handlers", []) or []:
                process_body(handler.body, collect_only)

    # First pass: locate the add-runs, so blank-node labels are only used
    # when every use of the blank node falls inside ONE run — `_:label` is
    # scoped to a single g{} island and fresh at each evaluation, so a node
    # shared across two islands must stay a Python BNode.
    run_spans: list[tuple[int, int]] = []
    process_body(tree.body, collect_only=True)
    for var in list(d.bnode_labels):
        uses = [n.lineno for n in ast.walk(tree)
                if isinstance(n, ast.Name) and n.id == var
                and isinstance(n.ctx, ast.Load)]
        if not uses or not any(lo <= min(uses) and max(uses) <= hi
                               for lo, hi in run_spans):
            del d.bnode_labels[var]
    # the BNode(...) assignments whose label survived are absorbed
    for stmt in ast.walk(tree):
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 \
                and isinstance(stmt.targets[0], ast.Name) \
                and stmt.targets[0].id in d.bnode_labels:
            drop_stmts.append(stmt)

    process_body(tree.body)

    # standalone term rewrites outside add-runs: line-level regexes for
    # URIRef("..."), NS.term, NS["term"], Literal(..., lang=...)
    edited_lines = set()
    for a, b, _ in edits:
        edited_lines.update(range(a, b + 1))

    out_lines = list(d.lines)
    for idx, line in enumerate(out_lines):
        if idx in edited_lines:
            continue
        new = line
        for var, (label, iri, _bare) in d.prefixes.items():
            if iri == RDF_NS:
                new = re.sub(rf"\b{re.escape(var)}\.type\b", f"{label}:type", new)
            new = re.sub(rf"\b{re.escape(var)}\.([A-Za-z_][\w]*)",
                         rf"{label}:\1", new)
            new = re.sub(rf"\b{re.escape(var)}\[(['\"])([A-Za-z_][\w.-]*)\1\]",
                         rf"{label}:\2", new)
        new = re.sub(r"\bURIRef\(\s*(['\"])([^'\"<>\s]+)\1\s*\)", r"<\2>", new)
        new = re.sub(r"\bLiteral\(\s*(['\"])(.*?)\1\s*,\s*lang=(['\"])(\w[\w-]*)\3\s*\)",
                     r'"\2"@\4', new)
        if new != line:
            out_lines[idx] = new

    # drop Namespace(...) assignment lines (replaced by @prefix)
    for stmt in drop_stmts:
        for ln in range(stmt.lineno - 1, stmt.end_lineno):
            if ln not in edited_lines:
                out_lines[ln] = None   # type: ignore[call-overload]

    # apply block edits (bottom-up)
    for a, b, text in sorted(edits, reverse=True):
        out_lines[a:b + 1] = [text]

    result_lines = [l for l in out_lines if l is not None]
    insert_at = _after_last_toplevel_import(result_lines)
    header = prefix_decls + [""] if prefix_decls else []
    result_lines[insert_at:insert_at] = header
    if d.prefixes:
        d.add_note("prefixes: " + ", ".join(
            f"{v}->{p[0]}" for v, p in d.prefixes.items()))
    if d.type_aliases:
        d.add_note("rdf:type aliases rendered as Turtle `a`: "
                   + ", ".join(sorted(d.type_aliases)))
    if d.bnode_labels:
        d.add_note("BNode labels absorbed into island labels (single-island "
                   "uses only): " + ", ".join(sorted(d.bnode_labels)))
    return "\n".join(result_lines) + "\n", d.notes


# --- example materialisation ------------------------------------------------

HEADER = """\
# Extracted from {repository}@{commit_short} : {path}
# region: {qualname} (lines {lineno}-{end_lineno}, band {band})
# licence of the source repository: see meta.json
"""

DRIVER_TEMPLATE = '''\
"""Validation driver for {region_id}.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry={entry!r},
    calls={calls},
)
'''


def _dedent_region(reg: dict) -> str:
    return textwrap.dedent(reg["source"])


def _module_resolver(reg: dict, config: dict):
    """Resolve an import of the region's own project to its source text."""
    from .acquire import repo_dir
    root = repo_dir(config, reg["repository"])
    here = (root / reg["path"]).parent

    def resolve(module: str, level: int) -> str | None:
        parts = module.split(".") if module else []
        base = here
        for _ in range(max(0, level - 1)):
            base = base.parent
        candidates = []
        if level:
            candidates += [base.joinpath(*parts).with_suffix(".py"),
                           base.joinpath(*parts, "__init__.py")]
        else:
            candidates += [root.joinpath(*parts).with_suffix(".py"),
                           root.joinpath(*parts, "__init__.py"),
                           here.joinpath(*parts).with_suffix(".py")]
        for cand in candidates:
            try:
                if cand.is_file() and root in cand.parents:
                    return cand.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
        return None

    return resolve


def materialise(reg: dict, config: dict) -> str:
    band_dir = EXAMPLES_DIR / reg["band"]
    ex_dir = band_dir / reg["region_id"]
    meta_path = ex_dir / "meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        if meta.get("translation_status") != "draft":
            return "kept"
        drafted = ex_dir / "translated.ldpy"
        if drafted.exists() and _sha(drafted.read_text()) != meta.get("draft_sha"):
            return "kept(hand-edited)"
    ex_dir.mkdir(parents=True, exist_ok=True)

    context = "\n".join(reg["context"])
    body = _dedent_region(reg)
    original = HEADER.format(commit_short=reg["commit"][:10], **reg)
    if context:
        original += context + "\n\n"
    original += body + "\n"
    (ex_dir / "original.py").write_text(original)

    draft, notes = draft_translation(original,
                                     resolve_module=_module_resolver(reg, config))
    (ex_dir / "translated.ldpy").write_text(draft)

    entry = reg["qualname"].split(".")[-1] if reg["kind"] == "function" else None
    (ex_dir / "driver.py").write_text(DRIVER_TEMPLATE.format(
        region_id=reg["region_id"], entry=entry,
        calls="[]  # TODO: [(args, kwargs), ...] fixtures" if entry else "None"))

    meta = {
        "region_id": reg["region_id"],
        "repository": reg["repository"],
        "commit": reg["commit"],
        "path": reg["path"],
        "qualname": reg["qualname"],
        "lineno": reg["lineno"], "end_lineno": reg["end_lineno"],
        "band": reg["band"],
        "kind": reg["kind"],
        "rdf_ops": reg["rdf_ops"],
        "categories": reg["categories"],
        "translation_status": "draft",
        "classification": None,
        "translation_notes": notes,
        "draft_sha": _sha(draft),
        "provenance": provenance(config),
    }
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    return "drafted"


def run(config: dict) -> None:
    regions = load_regions()
    counts: dict[str, int] = {}
    for reg in regions:
        status = materialise(reg, config)
        counts[status] = counts.get(status, 0) + 1
    print(f"translate: {counts}")

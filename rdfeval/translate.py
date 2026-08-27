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

class Draft:
    def __init__(self, source: str):
        self.source = source
        self.lines = source.splitlines()
        self.notes: list[str] = []
        self.replacements: list[tuple[int, int, int, int, str]] = []
        # var name -> prefix label
        self.prefixes: dict[str, tuple[str, str]] = {}   # var -> (label, iri)

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
            return f"{pref[0]}:{node.attr}"
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
        pref = d.prefixes.get(node.value.id)
        sl = node.slice
        if pref and isinstance(sl, ast.Constant) and isinstance(sl.value, str) \
                and PN_LOCAL_OK.match(sl.value):
            return f"{pref[0]}:{sl.value}"
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


def draft_translation(source: str) -> tuple[str, list[str]]:
    """Best-effort mechanical rewrite of an rdflib module into ldpy."""
    d = Draft(source)
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return source, [f"unparsable: {e}"]

    wk = well_known_iris()
    used = set(re.findall(r"[A-Za-z_][\w]*", source))
    prefix_decls: list[str] = []
    drop_stmts: list[ast.stmt] = []

    # namespaces: assignments and well-known imports
    for stmt in ast.walk(tree):
        if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
            fn = stmt.value.func
            name = fn.id if isinstance(fn, ast.Name) else (
                fn.attr if isinstance(fn, ast.Attribute) else None)
            if name == "Namespace" and stmt.value.args \
                    and isinstance(stmt.value.args[0], ast.Constant) \
                    and isinstance(stmt.value.args[0].value, str) \
                    and len(stmt.targets) == 1 \
                    and isinstance(stmt.targets[0], ast.Name):
                var = stmt.targets[0].id
                label = var.lower().rstrip("_")
                if not re.match(r"[a-z][\w-]*$", label):
                    continue
                d.prefixes[var] = (label, stmt.value.args[0].value)
                prefix_decls.append(f"@prefix {label}: <{stmt.value.args[0].value}> .")
                drop_stmts.append(stmt)
        elif isinstance(stmt, ast.ImportFrom) and (stmt.module or "").startswith("rdflib"):
            for alias in stmt.names:
                if alias.name in wk and (alias.asname or alias.name) in used:
                    var = alias.asname or alias.name
                    label = var.lower()
                    d.prefixes[var] = (label, wk[alias.name])
                    decl = f"@prefix {label}: <{wk[alias.name]}> ."
                    if decl not in prefix_decls:
                        prefix_decls.append(decl)

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

    def process_body(body: list[ast.stmt]) -> None:
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
                    process_body(sub)
            for handler in getattr(stmt, "handlers", []) or []:
                process_body(handler.body)

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
        for var, (label, _iri) in d.prefixes.items():
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
    # insert prefix declarations after the last import
    insert_at = 0
    for i, l in enumerate(result_lines):
        if re.match(r"\s*(import |from )", l or ""):
            insert_at = i + 1
    header = prefix_decls + [""] if prefix_decls else []
    result_lines[insert_at:insert_at] = header
    if d.prefixes:
        d.add_note("prefixes: " + ", ".join(
            f"{v}->{p[0]}" for v, p in d.prefixes.items()))
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

    draft, notes = draft_translation(original)
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

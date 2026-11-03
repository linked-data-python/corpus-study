"""Human validation by translation patterns (record corpus/403).

    python -m rdfeval patterns

A pair-by-pair review of some 380 regions, often dozens of lines each, will
not happen; most rewrites are instances of a small family of rules
(``g.add((s, p, o))`` → ``+{ s p o }``, ``g.value(s, p)`` →
``m{ s p ?o }.first()``…).  So the reviewer approves RULES, and a pair is
covered when every rewrite in it is an instance of approved rules.  This
stage:

1. **extracts** the rewrites of each selected pair mechanically: every
   island of ``translated.ldpy`` with the Python of ``original.py`` it
   replaces (line alignment, :func:`rewrites`);
2. **groups** them into rules: a *statement rule* — the island kind, how its
   result is consumed (``.first()``, ``bool(…)``, ``for … in``…) and the
   rdflib call of the hunk it replaces — and *term rules*, one per way a
   term is written (``RDF.type`` → ``a``, ``Literal(x, datatype=XSD.t)`` →
   ``{x}^^xsd:t``…) — :func:`rules_of`;
3. writes the review page ``results/review/patterns.html``: each rule with
   its conditions of use, its counts, its shortest real instances and the
   places where its rdflib call was kept in Python (counter-examples); the
   verdicts go into ``results/raw/pattern_verdicts.json``;
4. computes the **coverage** (:func:`coverage`): a pair is covered when its
   driver proves the equivalence, its classification is
   ``directly-expressible``, no hunk brings in Python names the original
   does not have (a restructuring), and all its rules are approved; every
   other pair goes to individual review, with the reason;
5. draws the **audit**: a seeded sample of covered pairs, to check what
   rules cannot see — the driver's strength, the shims, the context.

Before any verdict the coverage is computed twice: as it stands, and as it
would be with every rule approved — the bound the review of the rules can
reach.
"""

from __future__ import annotations

import builtins
import difflib
import html
import keyword
import json
import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field

from .config import RESULTS_RAW, RESULTS_SUMMARY, ROOT
from .constructions import NOT_SHIMS
from .ldpy_metrics import _ISLAND_TOKEN, island_spans

REVIEW_DIR = ROOT / "results" / "review"
PATTERNS_JSON = REVIEW_DIR / "patterns.json"
PATTERNS_HTML = REVIEW_DIR / "patterns.html"
# The verdicts are the reviewer's input, kept under version control like the
# audit's (results/review/ is generated and ignored).
VERDICTS = RESULTS_RAW / "pattern_verdicts.json"
COVERAGE = RESULTS_SUMMARY / "pattern_coverage.json"

VERDICT_VALUES = ("approved", "rejected", "needs-work")
AUDIT_SIZE = 20
AUDIT_SEED = 20261103
INSTANCES = 3

# rdflib calls a statement rule can replace, most specific first.
GRAPH_CALLS = ("value", "set", "addN", "add", "remove", "objects",
               "subjects", "predicates", "subject_objects",
               "predicate_objects", "subject_predicates", "triples",
               "items", "query", "update", "bind", "parse")

_CALL = re.compile(r"\.(\w+)\s*\(")
_CONTAINS = re.compile(r"\)\s*(?:not\s+)?in\s+[\w.\[\]()]+")
_INTRO = re.compile(r"^(?:[+\-msgef]|_:)?\{(.*)\}\s*(\([^()]*\))?\s*$", re.S)

# Conditions of use, written per rule: what the rule's equivalence rests on.
# A rule absent from here is shown with "conditions to write".
CONDITIONS = {
    "+{ } ← .add()": "Each `g.add((s, p, o))` becomes one triple; the "
        "graph is the one named in the call suffix `(g)` or by `@graph`.",
    "+{ } ← .addN()": "`addN` of quads into one graph only.",
    "+{ } ← .set()": "`g.set((s, p, o))` removes every `(s, p, *)` first: "
        "the translation must remove before it adds (`-{ s p ?o }`).",
    "-{ } ← .remove()": "`None` in the pattern is `?var` in the island; a "
        "ground triple stays ground.",
    "m{ }·first ← .value()": "`g.value(s, p)` without a non-`None` "
        "`default` and without `any=False` (which raises on two values); "
        "`.first()` returns `None` when nothing matches, as `value` does.",
    "m{ }·one ← .value()": "`g.value(s, p, any=False)`: `.one()` raises "
        "when there are several values, as `any=False` does.",
    "m{ }·bool ← contains": "`(s, p, o) in g` with ground terms, or `None` "
        "as a wildcard written `?var`.",
    "m{ }·truth ← contains": "Same as `bool(…)`: the match result is "
        "truthy when it has a row.",
    "m{ }·for ← .objects()": "One variable bound per row, in the object "
        "position; same multiset of rows (order unspecified in both).",
    "m{ }·for ← .subjects()": "One variable bound per row, in the subject "
        "position.",
    "m{ }·for ← .triples()": "The variables of the pattern, unpacked in "
        "the order they appear; `None` positions become variables.",
    "m{ }·for ← .predicate_objects()": "Two variables, unpacked in the "
        "order predicate, object.",
    "m{ }·for ← .subject_objects()": "Two variables, unpacked in the order "
        "subject, object.",
    "m{ }·count ← (no graph call)": "`.count()` counts rows of the match.",
    "s{ }·value ← .query()": "A query written as a literal string becomes "
        "an island: same text, prefixes from `@prefix` instead of "
        "`initNs`.",
    "s{ }·for ← .query()": "Iterating the result rows of a literal query.",
    "@prefix ← Namespace()": "`EX = Namespace(\"…\")` becomes "
        "`@prefix ex: <…>`; every `EX.x` becomes `ex:x`.",
    "@prefix ← .bind()": "`g.bind(\"ex\", EX)` becomes `@prefix`: the "
        "prefix is bound in the graphs the islands create.",
    "@graph as g ← g = Graph()": "`@graph as g` creates the graph `g` "
        "and makes it the current graph of the scope.",
    "@graph ← (receiver)": "`@graph g` names the graph the islands of the "
        "scope read and write: `g.` receivers disappear.",
    "term: a ← RDF.type": "`RDF.type` in predicate position is written "
        "`a`.",
    "term: p:l ← NS.l": "`NS.local` becomes `ns:local`, with `@prefix ns:` "
        "the namespace of `NS`.",
    "term: p:l ← NS['l']": "`NS['local']` becomes `ns:local` when `local` "
        "is a valid local name.",
    "term: {x} ← x": "A Python value that is already an RDF term is "
        "interpolated as it is.",
    "term: {x} ← Literal(x)": "`Literal(x)` becomes `{x}`: a Python value "
        "interpolated in a term position is converted as `Literal` does.",
    "term: {x}^^p:t ← Literal(x, datatype=)": "The lexical form is "
        "`str(x)` in both; `Literal(n, datatype=dt)` of a number is not "
        "`\"n\"^^dt` written by hand.",
    "term: {x}@l ← Literal(x, lang=)": "Language tag kept; `None` as a "
        "language raises in the island where rdflib drops it.",
    "term: \"s\" ← Literal(\"s\")": "A constant string becomes a plain "
        "literal.",
    "term: ; ← repeated subject": "Consecutive triples with the same "
        "subject share it with `;`; the order of the triples is kept.",
    "term: , ← repeated subject and predicate": "Consecutive objects of "
        "the same subject and predicate share them with `,`.",
    "term: [ ] ← BNode()": "A blank node created only to hang triples on "
        "becomes `[ … ]`: it must not be used elsewhere.",
    "term: <iri> ← URIRef('…')": "A constant `URIRef` becomes `<…>`.",
    "f<…> ← URIRef(f'…')": "`URIRef(f\"…{x}…\")` becomes `f<…{x}…>`: "
        "same string, same IRI.",
}


@dataclass
class Rewrite:
    """One island of a translation and the Python it replaces."""
    region_id: str
    kind: str
    line: int                      # 1-based, in translated.ldpy
    island: str
    before: str                    # the island's line, before it
    after: str                     # the island's line, after it
    python: str                    # the original lines of its hunk
    ldpy: str                      # the translated lines of its hunk
    rules: list = field(default_factory=list)


def _hunks(orig: str, ldpy: str):
    a = [line.strip() for line in orig.splitlines()]
    b = [line.strip() for line in ldpy.splitlines()]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    return [op for op in sm.get_opcodes() if op[0] != "equal"]


def _hunk_of(hunks, line0: int):
    for op in hunks:
        if op[3] <= line0 < max(op[4], op[3] + 1):
            return op
    return None


def rewrites(region_id: str, orig: str, ldpy: str) -> list[Rewrite]:
    """The islands of ``ldpy``, each with the original hunk it replaces."""
    ol, ll = orig.splitlines(), ldpy.splitlines()
    hunks = _hunks(orig, ldpy)
    out = []
    for (l0, c0, l1, c1, kind) in island_spans(ldpy):
        if kind.endswith("-close"):
            continue
        if l0 == l1:
            text = ll[l0][c0:c1]
        else:
            text = "\n".join([ll[l0][c0:]] + ll[l0 + 1:l1] + [ll[l1][:c1]])
        op = _hunk_of(hunks, l0)
        py = "\n".join(x.strip() for x in ol[op[1]:op[2]]) if op else ""
        lp = "\n".join(x.strip() for x in ll[op[3]:op[4]]) if op else ""
        out.append(Rewrite(region_id, kind.removeprefix("island:"), l0 + 1,
                           text, ll[l0][:c0].strip(), ll[l1][c1:].strip(),
                           py, lp))
    return out


# ---------------------------------------------------------------- rules

def _calls(python: str) -> list[str]:
    found = {m.group(1) for m in _CALL.finditer(python)}
    calls = [c for c in GRAPH_CALLS if c in found]
    if _CONTAINS.search(python):
        calls.append("contains")
    return calls


def consumption(before: str, after: str) -> str:
    """How the value of a reading island is used, from its line."""
    after = re.sub(r"^\([^()]*\)", "", after)       # a call suffix (g)
    if re.match(r"\.first\(\)", after):
        return "first"
    if re.match(r"\.one\(\)", after):
        return "one"
    if re.match(r"\.count\(\)", after):
        return "count"
    if re.match(r"\.execute\(", after):
        return "execute"
    if re.search(r"\bbool\($", before):
        return "bool"
    if re.search(r"\bfor\b.*\bin$", before):
        return "for"
    if re.search(r"next\(iter\($", before):
        return "next"
    if re.search(r"\b(list|set|sorted|tuple|frozenset)\($", before):
        return "collect"
    if re.search(r"(^|\b)(if|elif|while|assert|not|and|or)$", before):
        return "truth"
    return "value"


# For a reading island, the rdflib call it most likely replaces, by how its
# value is used: a hunk often holds several calls.
_READ_ORDER = {
    "first": ("value", "objects", "subjects", "triples", "query"),
    "one": ("value", "objects", "subjects", "triples", "query"),
    "next": ("value", "objects", "subjects", "triples", "query"),
    "bool": ("contains", "triples", "value", "objects", "subjects",
             "predicates", "query"),
    "truth": ("contains", "triples", "value", "objects", "subjects",
              "predicates", "query"),
}
_READ_DEFAULT = ("objects", "subjects", "predicates", "subject_objects",
                 "predicate_objects", "subject_predicates", "triples",
                 "items", "query", "update", "value", "contains")

_RDFLIB_NS = {"RDF", "RDFS", "OWL", "XSD", "SKOS", "DC", "DCTERMS", "FOAF",
              "PROV", "SH", "SOSA", "SSN", "TIME", "VOID", "DCAT", "ORG",
              "SDO", "SCHEMA", "QB", "ODRL2", "DOAP", "GEO", "DCMITYPE",
              "DCAM", "BRICK", "CSVW", "PROF", "VANN", "WGS"}


def _prefix_rule(island: str, orig: str) -> str:
    m = re.match(r"@prefix\s+([\w-]*):\s*<([^>]*)>", island)
    if not m:
        return "@prefix ← (none)"
    name, iri = m.groups()
    if re.search(rf"Namespace\(\s*[rRuU]?['\"]{re.escape(iri)}['\"]", orig):
        return "@prefix ← Namespace()"
    if re.search(rf"\.bind\(\s*['\"]{re.escape(name)}['\"]", orig):
        return "@prefix ← .bind()"
    if name.upper() in _RDFLIB_NS and re.search(
            rf"\b{name.upper()}\b", orig):
        return "@prefix ← rdflib namespace"
    if iri and iri in orig:
        return "@prefix ← IRIs written in full"
    if name and re.search(rf"\b{re.escape(name)}\b", orig, re.I):
        return "@prefix ← namespace defined outside the region"
    return "@prefix ← (none)"


def _statement_rule(rw: Rewrite, orig: str = "") -> str:
    calls = _calls(rw.python) or _calls(orig)
    kind = rw.kind
    if kind in ("addto", "graph"):
        island = "+{ }" if kind == "addto" else "g{ }"
        for c in ("set", "addN", "add"):
            if c in calls:
                return f"{island} ← .{c}()"
        return f"{island} ← {'.' + calls[0] + '()' if calls else '(no graph call)'}"
    if kind == "removefrom":
        for c in ("remove", "set"):
            if c in calls:
                return f"-{{ }} ← .{c}()"
        return "-{ } ← (no graph call)"
    if kind in ("match", "sparql", "fnode"):
        island = {"match": "m{ }", "sparql": "s{ }", "fnode": "f{ }"}[kind]
        use = consumption(rw.before, rw.after)
        order = _READ_ORDER.get(use, _READ_DEFAULT)
        hunk = _calls(rw.python)
        read = [c for c in order if c in hunk] or \
            [c for c in order if c in _calls(orig)]
        src = ("contains" if read[0] == "contains" else f".{read[0]}()") \
            if read else "(no graph call)"
        return f"{island}·{use} ← {src}"
    if kind == "prefix":
        return _prefix_rule(rw.island, orig or rw.python)
    if kind == "import":
        return "from … import p: ← import"
    if kind == "graph-decl":
        if rw.island.lstrip().startswith("@graph as"):
            return "@graph as g ← g = Graph()"
        return "@graph ← (receiver)"
    if kind in ("for-bindings", "bindings-decl"):
        return f"@bindings ← {'.' + calls[0] + '()' if calls else 'loop'}"
    if kind == "firi":
        return "f<…> ← URIRef(f'…')" if re.search(r"URIRef\(\s*f", rw.python) \
            else "f<…> ← string building"
    if kind == "iri":
        return "term: <iri> ← URIRef('…')" if "URIRef(" in rw.python \
            else "term: <iri> ← string"
    if kind == "pname":
        return _pname_rule(rw.island, rw.python, orig)
    if kind == "literal":
        return "term: literal outside island"
    return f"{kind}"


def _pname_rule(pname: str, python: str, orig: str = "") -> str:
    """How the original writes a prefixed name: looked for in the hunk,
    then in the whole original (the hunk is a line alignment, and the term
    may sit on a line it matched as unchanged)."""
    rule = _pname_in(pname, python)
    if rule.endswith("(other)") and orig:
        rule = _pname_in(pname, orig)
    return rule


def _pname_in(pname: str, python: str) -> str:
    local = pname.split(":", 1)[1] if ":" in pname else pname
    local = re.sub(r"\\(.)", r"\1", local)      # Turtle escapes: `Coding\.system`
    if pname.endswith(":{"):
        return "term: p:{x} ← NS[x]"
    if re.search(rf"(?<![\w:]){re.escape(pname)}(?![\w:])", python):
        return "term: p:l ← p:l (in a query string)"
    if local and re.search(rf"\b[A-Za-z_]\w*\.{re.escape(local)}\b", python):
        return "term: p:l ← NS.l"
    if local and re.search(rf"\[\s*['\"]{re.escape(local)}['\"]\s*\]",
                           python):
        return "term: p:l ← NS['l']"
    if local and re.search(rf"URIRef\(\s*['\"][^'\"]*{re.escape(local)}['\"]",
                           python):
        return "term: p:l ← URIRef('…')"
    if re.search(rf"\.term\(\s*['\"]{re.escape(local)}", python):
        return "term: p:l ← NS.term('l')"
    return "term: p:l ← (other)"


def _interp_end(text: str, i: int) -> int:
    depth, j = 0, i
    while j < len(text):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    return j


def _term_rules(body: str, python: str, orig: str = "") -> set[str]:
    rules = set()
    i, triples = 0, 0
    while i < len(body):
        m = _ISLAND_TOKEN.match(body, i)
        if m is None or body[i].isspace():
            i += 1
            continue
        if m.group("interp"):
            j = _interp_end(body, i)
            expr = body[i + 1:j - 1].strip()
            k = j
            while k < len(body) and body[k] == " ":
                k += 1
            esc = re.escape(expr)
            if body.startswith("^^", k):
                rules.add("term: {x}^^p:t ← Literal(x, datatype=)"
                          if re.search(rf"Literal\(\s*{esc}\s*,\s*datatype",
                                       python)
                          else "term: {x}^^p:t ← (other)")
            elif body.startswith("@", k):
                rules.add("term: {x}@l ← Literal(x, lang=)"
                          if re.search(rf"Literal\(\s*{esc}\s*,\s*lang",
                                       python)
                          else "term: {x}@l ← (other)")
            elif re.search(rf"Literal\(\s*{esc}\s*\)", python):
                rules.add("term: {x} ← Literal(x)")
            elif re.search(rf"URIRef\(\s*{esc}\s*\)", python):
                rules.add("term: {x} ← URIRef(x)")
            else:
                rules.add("term: {x} ← x")
            i = j
            continue
        g = m.lastgroup
        tok = m.group(0)
        if m.group("string"):
            suf = m.group("strsuffix") or ""
            if suf.startswith("^^"):
                rules.add("term: \"s\"^^p:t ← Literal(\"s\", datatype=)")
            elif suf.startswith("@"):
                rules.add("term: \"s\"@l ← Literal(\"s\", lang=)")
            else:
                rules.add("term: \"s\" ← Literal(\"s\")"
                          if "Literal(" in python else "term: \"s\" ← \"s\"")
        elif g == "pname" and tok == "a":
            rules.add("term: a ← RDF.type"
                      if re.search(r"\bRDF\.type\b", python or orig)
                      or re.search(r"\bRDF\.type\b", orig)
                      else "term: a ← rdf:type written otherwise")
        elif g == "pname" and ":" in tok:
            local_interp = tok.endswith(":") and body.startswith("{", m.end())
            rules.add(_pname_rule(tok + "{" if local_interp else tok,
                                  python, orig))
        elif g == "iri":
            rules.add("term: <iri> ← URIRef('…')" if "URIRef(" in python
                      else "term: <iri> ← string")
        elif g == "number":
            rules.add("term: n ← Literal(n)" if "Literal(" in python
                      else "term: n ← n")
        elif g == "blank":
            rules.add("term: _:b ← BNode('b')")
        elif g == "punct" and tok == ";":
            rules.add("term: ; ← repeated subject")
        elif g == "punct" and tok == ",":
            rules.add("term: , ← repeated subject and predicate")
        elif g == "punct" and tok == "[":
            rules.add("term: [ ] ← BNode()")
        elif g == "punct" and tok == ".":
            triples += 1
        elif g == "punct" and tok == "(":
            rules.add("term: ( ) ← Collection")
        i = m.end()
    if triples and not body.rstrip().endswith(".") or triples > 1:
        rules.add("term: . ← several triples")
    return rules


def rules_of(rw: Rewrite, orig: str = "") -> list[str]:
    """The statement rule of a rewrite, then its term rules, sorted."""
    rules = [_statement_rule(rw, orig)]
    m = _INTRO.match(rw.island)
    if m and rw.kind in ("addto", "removefrom", "match", "graph"):
        rules += sorted(_term_rules(m.group(1), rw.python, orig))
        if m.group(2) or re.match(r"\([^()]*\)", rw.after):
            rules.append("(g) ← receiver")
    return rules


# ------------------------------------------------------------ residual

_NAME = re.compile(r"\b[A-Za-z_]\w*\b")
_STRINGS = re.compile(r"(\"\"\"[\s\S]*?\"\"\"|'''[\s\S]*?'''"
                      r"|\"(?:[^\"\\\n]|\\.)*\"|'(?:[^'\\\n]|\\.)*')")
_COMMENT = re.compile(r"#[^\n]*")


# Names a translation may bring in without restructuring anything: keywords,
# builtins, the ldpy runtime, the island suffixes, and what rdflib exports
# (an import of `URIRef` the original reached as `rdflib.URIRef`).
_NOT_NEW = (set(keyword.kwlist) | set(dir(builtins))
            | {"ldpy", "ANY", "first", "one", "count", "execute", "rdflib",
               "URIRef", "Literal", "BNode", "Graph", "Namespace", "Dataset",
               "ConjunctiveGraph", "Variable"} | _RDFLIB_NS)


def _code_names(text: str) -> set[str]:
    return set(_NAME.findall(_COMMENT.sub("", _STRINGS.sub('""', text))))


def residual(orig: str, ldpy: str) -> list[str]:
    """Python names the translation introduces, outside its islands.

    A rule rewrites rdflib calls into islands; a name the original never
    uses — a helper, a table, a new variable — is a restructuring, which no
    rule covers.  Island text, strings and comments are left out."""
    spans = island_spans(ldpy)
    lines = ldpy.splitlines()
    for (l0, c0, l1, c1, _kind) in sorted(spans, reverse=True):
        if l0 == l1:
            lines[l0] = lines[l0][:c0] + " " + lines[l0][c1:]
        else:
            lines[l0] = lines[l0][:c0]
            for k in range(l0 + 1, l1):
                lines[k] = ""
            lines[l1] = " " + lines[l1][c1:]
    known = _code_names(orig) | _NOT_NEW
    return sorted(_code_names("\n".join(lines)) - known)


# ------------------------------------------------------------ the stage

def _selection() -> set[str] | None:
    from .aggregate import _reprise_selection
    sel = _reprise_selection()
    return {r for _, s in sel.values() for r in s} if sel else None


def collect(selected: set[str] | None = None) -> list[dict]:
    """Every selected final pair, with its rewrites and checks."""
    from .validate import iter_examples
    pairs = []
    for ex_dir, meta in iter_examples():
        rid = meta["region_id"]
        if meta.get("translation_status") != "final":
            continue
        if selected is not None and rid not in selected:
            continue
        orig, tr = ex_dir / "original.py", ex_dir / "translated.ldpy"
        if not (orig.exists() and tr.exists()):
            continue
        o, t = orig.read_text(), tr.read_text()
        rws = rewrites(rid, o, t)
        for rw in rws:
            rw.rules = rules_of(rw, o)
        shims = sorted(p.name for p in ex_dir.glob("*.py")
                       if p.name not in NOT_SHIMS)
        pairs.append({
            "region_id": rid, "dir": str(ex_dir.relative_to(ROOT)),
            "classification": meta.get("classification"),
            "validation": (meta.get("validation") or {}).get("status"),
            "rewrites": rws, "residual": residual(o, t), "shims": shims,
            "kept": _kept_calls(t),
        })
    return pairs


def _kept_calls(ldpy: str) -> dict[str, list[str]]:
    """rdflib calls a translation kept in Python: the counter-examples of
    the rules that would have rewritten them."""
    out = defaultdict(list)
    for line in ldpy.splitlines():
        s = line.strip()
        if s.startswith("#"):
            continue
        for c in _calls(s):
            if c in ("add", "remove", "set") and f".{c}((" not in s:
                continue                  # a set's add, a list's remove
            if c == "contains" and not re.search(r",[^()]*\)\s*in\b", s):
                continue                  # not a triple pattern
            if c in ("value", "objects", "subjects", "triples", "add",
                     "remove", "query", "set", "contains",
                     "predicate_objects", "subject_objects"):
                out[c].append(s)
    return dict(out)


def load_verdicts() -> dict[str, dict]:
    if not VERDICTS.exists():
        return {}
    data = json.loads(VERDICTS.read_text())
    return {k: v for k, v in data.get("rules", {}).items()
            if v.get("verdict") in VERDICT_VALUES}


def coverage(pairs: list[dict], approved: set[str] | None) -> dict:
    """Per pair: covered, or the reasons it goes to individual review.

    ``approved`` None means every rule approved — the bound."""
    out = {}
    for p in pairs:
        reasons = []
        if p["validation"] != "equivalent":
            reasons.append(f"validation: {p['validation']}")
        if p["classification"] != "directly-expressible":
            reasons.append(f"classification: {p['classification']}")
        if p["residual"]:
            reasons.append("restructuring: " + ", ".join(p["residual"][:6]))
        if not p["rewrites"]:
            reasons.append("no island")
        rules = {r for rw in p["rewrites"] for r in rw.rules}
        if approved is not None:
            missing = sorted(rules - approved)
            if missing:
                reasons.append("rules not approved: " + "; ".join(missing))
        out[p["region_id"]] = reasons
    return out


def rule_table(pairs: list[dict]) -> dict[str, dict]:
    """Each rule with its counts, shortest instances and counter-examples."""
    table: dict[str, dict] = {}
    for p in pairs:
        for rw in p["rewrites"]:
            for r in rw.rules:
                t = table.setdefault(r, {"occurrences": 0, "pairs": set(),
                                         "instances": []})
                t["occurrences"] += 1
                t["pairs"].add(p["region_id"])
                t["instances"].append(rw)
    kept_by_call = defaultdict(list)
    for p in pairs:
        for call, lines in p["kept"].items():
            kept_by_call[call] += [(p["dir"], s) for s in lines]
    out = {}
    for r, t in table.items():
        inst = sorted(t["instances"],
                      key=lambda rw: (len(rw.python) + len(rw.ldpy),
                                      rw.region_id))
        seen, chosen = set(), []
        for rw in inst:
            if rw.region_id in seen or not rw.python:
                continue
            seen.add(rw.region_id)
            chosen.append({"region_id": rw.region_id, "line": rw.line,
                           "python": rw.python, "ldpy": rw.ldpy})
            if len(chosen) == INSTANCES:
                break
        m = re.search(r"← \.(\w+)\(\)|← (contains)$", r)
        call = (m.group(1) or m.group(2)) if m else None
        counter = sorted(kept_by_call.get(call, []),
                         key=lambda x: len(x[1]))[:INSTANCES] if call else []
        out[r] = {"occurrences": t["occurrences"],
                  "pairs": sorted(t["pairs"]),
                  "conditions": CONDITIONS.get(r),
                  "instances": chosen,
                  "kept_in_python": [{"dir": d, "line": s}
                                     for d, s in counter],
                  "kept_count": len(kept_by_call.get(call, []))
                  if call else 0}
    return dict(sorted(out.items(),
                       key=lambda kv: (-len(kv[1]["pairs"]), kv[0])))


def unlocks(pairs: list[dict], cov_bound: dict) -> dict[str, int]:
    """For each rule, the pairs it alone keeps from the bound: covered when
    every rule is approved, and holding that rule."""
    count = Counter()
    for p in pairs:
        if cov_bound[p["region_id"]]:
            continue
        for r in {r for rw in p["rewrites"] for r in rw.rules}:
            count[r] += 1
    return dict(count)


def audit_draw(covered: list[str], size: int = AUDIT_SIZE,
               seed: int = AUDIT_SEED) -> list[str]:
    """A seeded sample of covered pairs; the same seed on the same covered
    set gives the same draw."""
    rng = random.Random(seed)
    pool = sorted(covered)
    return sorted(rng.sample(pool, min(size, len(pool))))


def run(config: dict | None = None) -> dict:
    pairs = collect(_selection())
    table = rule_table(pairs)
    verdicts = load_verdicts()
    approved = {r for r, v in verdicts.items() if v["verdict"] == "approved"}
    bound = coverage(pairs, None)
    now = coverage(pairs, approved)
    need = unlocks(pairs, bound)
    for r, t in table.items():
        t["covers_pairs"] = need.get(r, 0)
        t["verdict"] = verdicts.get(r, {}).get("verdict")
        t["comment"] = verdicts.get(r, {}).get("comment")
    covered = sorted(r for r, why in now.items() if not why)
    covered_bound = sorted(r for r, why in bound.items() if not why)
    individual = Counter()
    for why in bound.values():
        for w in why:
            individual[w.split(":")[0]] += 1
    summary = {
        "pairs": len(pairs),
        "rules": len(table),
        "rules_judged": len(verdicts),
        "rules_approved": len(approved),
        "covered": len(covered),
        "covered_if_all_approved": len(covered_bound),
        "individual_review_reasons": dict(individual),
        "audit": {"seed": AUDIT_SEED, "size": AUDIT_SIZE,
                  "drawn_from": "covered" if covered else
                  "covered_if_all_approved",
                  "regions": audit_draw(covered or covered_bound)},
        "per_pair": {r: (why or ["covered"]) for r, why in now.items()},
        "per_pair_if_all_approved": {r: (why or ["covered"])
                                     for r, why in bound.items()},
    }
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    PATTERNS_JSON.write_text(json.dumps(table, indent=1, ensure_ascii=False),
                             encoding="utf-8")
    COVERAGE.write_text(json.dumps(summary, indent=1, ensure_ascii=False),
                        encoding="utf-8")
    if not VERDICTS.exists():
        VERDICTS.write_text(json.dumps(
            {"reviewer": None, "rules": {r: {"verdict": None, "comment": None}
                                         for r in table}},
            indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    PATTERNS_HTML.write_text(render(table, summary), encoding="utf-8")
    print(f"patterns: {len(pairs)} pairs, {len(table)} rules "
          f"({len(approved)} approved); covered {len(covered)}, "
          f"{len(covered_bound)} if every rule is approved")
    print(f"  individual review, by reason (bound): {dict(individual)}")
    print(f"  page: {PATTERNS_HTML.relative_to(ROOT)}")
    return summary


# ------------------------------------------------------------ the page

def _esc(s) -> str:
    return html.escape(str(s or ""))


def render(table: dict, summary: dict) -> str:
    cards = []
    for i, (rule, t) in enumerate(table.items()):
        inst = "".join(
            f"<div class=inst><div class=src>{_esc(x['region_id'][:90])}"
            f" · l. {x['line']}</div><div class=pair>"
            f"<pre class=py>{_esc(x['python'])}</pre>"
            f"<pre class=ld>{_esc(x['ldpy'])}</pre></div></div>"
            for x in t["instances"])
        kept = "".join(f"<li><code>{_esc(k['line'][:140])}</code></li>"
                       for k in t["kept_in_python"])
        kept_block = (f"<details><summary>kept in Python elsewhere: "
                      f"{t['kept_count']}</summary><ul>{kept}</ul></details>"
                      if t["kept_count"] else "")
        cond = _esc(t["conditions"]) if t["conditions"] \
            else "<em>conditions to write</em>"
        radios = "".join(
            f"<label><input type=radio name=r{i} value={v}"
            f"{' checked' if t.get('verdict') == v else ''}> {v}</label>"
            for v in VERDICT_VALUES)
        cards.append(
            f"<section class=rule data-rule=\"{_esc(rule)}\" data-i={i}>"
            f"<h2>{_esc(rule)}</h2><p class=counts>{t['occurrences']} "
            f"occurrences in {len(t['pairs'])} pairs · needed by "
            f"{t['covers_pairs']} pairs otherwise covered</p>"
            f"<p class=cond>{cond}</p>{inst}{kept_block}"
            f"<div class=verdict>{radios}<input class=comment "
            f"placeholder=comment value=\"{_esc(t.get('comment'))}\"></div>"
            f"</section>")
    s = summary
    head = (f"<p>{s['pairs']} pairs, {s['rules']} rules, "
            f"{s['rules_approved']} approved. Covered now: {s['covered']}; "
            f"with every rule approved: {s['covered_if_all_approved']}. "
            f"Individual review (with every rule approved): "
            f"{_esc(s['individual_review_reasons'])}.</p>")
    return PAGE.replace("{{HEAD}}", head).replace("{{CARDS}}",
                                                  "\n".join(cards))


PAGE = """<!doctype html>
<html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width, initial-scale=1">
<title>Translation patterns</title>
<style>
:root{--bg:#fff;--fg:#1d1d1f;--mut:#666;--card:#f6f6f8;--py:#fff6ec;
--ld:#eef6ff;--line:#ddd}
@media (prefers-color-scheme:dark){:root{--bg:#161618;--fg:#e8e8ea;
--mut:#999;--card:#222226;--py:#2c2318;--ld:#17222e;--line:#333}}
body{background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,
sans-serif;margin:0 auto;max-width:1100px;padding:16px}
h1{font-size:1.4em}.rule{background:var(--card);border:1px solid
var(--line);border-radius:8px;padding:12px 16px;margin:16px 0}
h2{font:600 1.05em ui-monospace,monospace;margin:0 0 4px}
.counts,.src{color:var(--mut);font-size:.85em}.cond{margin:6px 0 10px}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:8px}
@media (max-width:700px){.pair{grid-template-columns:1fr}}
pre{margin:0;padding:8px;border-radius:6px;overflow-x:auto;
font-size:.8em;white-space:pre-wrap}.py{background:var(--py)}
.ld{background:var(--ld)}.inst{margin:8px 0}
.verdict{margin-top:10px;display:flex;gap:14px;flex-wrap:wrap;
align-items:center}.comment{flex:1;min-width:200px}
#bar{position:sticky;top:0;background:var(--bg);padding:8px 0;
border-bottom:1px solid var(--line)}
</style></head><body>
<h1>Translation patterns — human validation (record corpus/403)</h1>
<div id=bar>{{HEAD}}<button id=export>Export verdicts</button>
<span id=n></span></div>
<p>Approve a rule when every instance of it, under its conditions, is the
translation a competent user would write and is equivalent. Verdicts are
kept in this browser until exported: save the file as
<code>results/raw/pattern_verdicts.json</code>, then rerun
<code>rdfeval patterns</code>.</p>
{{CARDS}}
<script>
const KEY='ldpy-pattern-verdicts';
let saved={};try{saved=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
const secs=[...document.querySelectorAll('.rule')];
function state(){const o={};for(const s of secs){const r=s.dataset.rule;
const c=s.querySelector('input[type=radio]:checked');
const m=s.querySelector('.comment').value||null;
o[r]={verdict:c?c.value:null,comment:m}}return o}
function count(){const o=state();document.getElementById('n').textContent=
' '+Object.values(o).filter(v=>v.verdict).length+' / '+secs.length+' judged'}
for(const s of secs){const v=saved[s.dataset.rule];if(v){if(v.verdict){
const i=s.querySelector('input[value="'+v.verdict+'"]');if(i)i.checked=true}
if(v.comment)s.querySelector('.comment').value=v.comment}
s.addEventListener('input',()=>{try{localStorage.setItem(KEY,
JSON.stringify(state()))}catch(e){}count()})}
count();
document.getElementById('export').onclick=()=>{const blob=new Blob(
[JSON.stringify({reviewer:null,rules:state()},null,1)+'\\n'],
{type:'application/json'});const a=document.createElement('a');
a.href=URL.createObjectURL(blob);a.download='pattern_verdicts.json';a.click()};
</script></body></html>
"""

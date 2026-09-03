"""Surface and structure metrics for Linked-Data Python sources.

The ldpy transpiler's LanguageMap tells us exactly which source spans are RDF
islands (segments of kind ``island:*``); everything else is plain Python.
Metrics are then defined as:

tokens
    Python tokens of the source with every island replaced by a one-token
    placeholder, minus the placeholders, plus *island tokens* (Turtle-level
    tokenisation: IRIs, prefixed names, literals with their language/datatype
    glued suffix, numbers, ``a``, blank-node labels, variables, punctuation,
    and ``{...}`` interpolations, whose interior is tokenised as Python).

syntax_nodes
    Positioned AST nodes of the placeholder-masked source (each island
    counts 1 placeholder node), minus the placeholders, plus *island
    structure nodes*: one node per RDF term + one per asserted triple +
    one per blank-node property list, collection, or prefix/base
    declaration, plus the Python AST nodes of interpolated expressions.
    This mirrors the AST-node census of the Python side (rdfeval.analyze):
    a triple expressed as ``g.add((s, p, o))`` costs Call+Attribute+Name+
    Tuple+terms there; here ``s p o`` costs 1 triple node + its terms.

islands, island_chars, terms, triples_expressed, scaffolding_tokens
    See ``IslandStats``.  ``triples_expressed`` counts explicit
    predicate–object assertions (collection/list expansion triples are NOT
    counted — the Python side's ``triples_added`` counts ``g.add`` calls,
    which is the comparable notion).  Both islands that ASSERT count:
    ``g{ }`` and ``+{ }``.

patterns_expressed, patterns_semantic
    Triple *patterns* — what ``-{ }`` removes and ``m{ }`` matches.  They are
    counted apart from assertions on purpose: a pattern with a wildcard is
    not a triple, and pooling the two would corrupt every per-triple ratio.
    Their Python counterpart is ``g.remove((s, p, None))`` and the selector
    calls, not ``g.add``.

Failures are explicit: a source the transpiler rejects raises LdpyMetricsError.
"""

from __future__ import annotations

import ast
import io
import re
import tokenize
from dataclasses import dataclass, field


class LdpyMetricsError(Exception):
    pass


def _transpile(source: str):
    try:
        from ldpy.transpiler import transpile
    except ImportError as e:
        raise LdpyMetricsError(f"ldpy not importable: {e}") from e
    try:
        return transpile(source)
    except SyntaxError as e:
        raise LdpyMetricsError(f"transpile failed: {e}") from e


def island_spans(source: str) -> list[tuple[int, int, int, int, str]]:
    """(line0, col0, line1, col1, kind) for each island, 0-based, end-exclusive."""
    r = _transpile(source)
    spans = []
    for seg in r.map.segments:
        if seg.kind.startswith("island") and seg.src is not None:
            spans.append((*seg.src, seg.kind))
    # segments are ordered; merge duplicates (several gen segments may map to
    # one src region)
    merged: list[tuple[int, int, int, int, str]] = []
    for sp in spans:
        if merged and merged[-1][:4] == sp[:4]:
            continue
        merged.append(sp)
    return merged


def _offset(lines_idx: list[int], line: int, col: int) -> int:
    return lines_idx[line] + col


def _line_index(source: str) -> list[int]:
    idx = [0]
    for ln in source.splitlines(keepends=True):
        idx.append(idx[-1] + len(ln))
    return idx


# --- island tokenisation ----------------------------------------------------

_ISLAND_TOKEN = re.compile(r"""
    (?P<comment>\#[^\n]*)
  | (?P<string>("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'))
        (?P<strsuffix>@[A-Za-z][A-Za-z0-9-]*|\^\^[^\s;,.\])}]+)?
  | (?P<iri><[^<>\s{}]*(?:\{[^}]*\}[^<>\s{}]*)*>)
  | (?P<interp>\{)              # interpolation start: handled by brace scan
  | (?P<blank>_:[\w.-]*)
  | (?P<var>[?$][A-Za-z_][\w]*)
  | (?P<number>[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)
  | (?P<pname>[A-Za-z_][\w.-]*:[\w.\-·]*|[A-Za-z_][\w.-]*)   # pname or bare 'a'
  | (?P<punct>[;,.\[\]()@^])
  | (?P<other>\S)
""", re.VERBOSE)

TERM_GROUPS = {"string", "iri", "blank", "var", "number"}


@dataclass
class IslandStats:
    tokens: int = 0
    terms: int = 0
    triples: int = 0
    structures: int = 0          # bnode property lists, collections, decls
    interp_py_tokens: int = 0
    interp_py_nodes: int = 0
    term_tokens: int = 0         # tokens that are part of RDF terms
    depth_sum: int = 0           # summed bracket depth of terms (nesting proxy)


def _python_tokens(text: str) -> int:
    from .analyze import SIGNIFICANT_TOKENS
    n = 0
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type in SIGNIFICANT_TOKENS and tok.string.strip():
                n += 1
    except (tokenize.TokenError, IndentationError, SyntaxError):
        n += len(re.findall(r"\S+", text))
    return n


def _python_nodes(text: str) -> int:
    from .analyze import _count_nodes
    try:
        return _count_nodes(ast.parse(text, mode="eval"))
    except SyntaxError:
        try:
            return _count_nodes(ast.parse(text))
        except SyntaxError:
            return 1


def _scan_interpolation(text: str, i: int) -> int:
    """Return index just past the matching '}' (text[i] == '{')."""
    depth = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c in "\"'":
            q = c
            i += 1
            while i < n and text[i] != q:
                i += 2 if text[i] == "\\" else 1
            i += 1
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return n


def tokenize_island(text: str, kind: str, stats: IslandStats) -> None:
    """Tokenise one island's source text into stats (additive)."""
    # strip the introducer so g{ ... } contributes its braces as punctuation
    depth = 0
    i, n = 0, len(text)
    pending_subject = True
    obj_position = False        # inside a predicate-object list, expecting object
    while i < n:
        m = _ISLAND_TOKEN.match(text, i)
        if not m:
            i += 1
            continue
        g = m.lastgroup
        tok = m.group(0)
        if g == "comment":
            i = m.end()
            continue
        if g == "interp":
            end = _scan_interpolation(text, i)
            inner = text[i + 1:end - 1]
            # glued suffix? {expr}@lang / {expr}^^dt
            suffix = re.match(r"@[A-Za-z][A-Za-z0-9-]*|\^\^\S+", text[end:end + 40])
            stats.tokens += 1                       # the interpolation itself
            stats.terms += 1
            stats.term_tokens += 1
            stats.depth_sum += max(depth - 1, 0)
            stats.interp_py_tokens += _python_tokens(inner)
            stats.interp_py_nodes += _python_nodes(inner)
            i = end + (suffix.end() if suffix else 0)
            continue
        stats.tokens += 1
        if g in TERM_GROUPS:
            stats.terms += 1
            stats.term_tokens += 1 + (1 if m.group("strsuffix") else 0)
            if m.group("strsuffix"):
                stats.tokens += 1
            stats.depth_sum += max(depth - 1, 0)
        elif g == "pname":
            # bare Turtle keyword 'a' is a term; a lone prefix decl name is not
            stats.terms += 1
            stats.term_tokens += 1
            stats.depth_sum += max(depth - 1, 0)
        elif g == "punct":
            if tok == "[":
                depth += 1
                stats.structures += 1
            elif tok == "(":
                depth += 1
                stats.structures += 1
            elif tok in "])":
                depth -= 1
        i = m.end()


def _turtle_tokens(text: str):
    """Minimal token stream over a g{} body: TERM, '[', ']', '(', ')', ';',
    ',', '.'  (strings, IRIs and interpolations are single TERMs)."""
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1
        elif c == "#":
            while i < n and text[i] != "\n":
                i += 1
        elif c in "\"'":
            q = c
            j = i + 1
            while j < n and text[j] != q:
                j += 2 if text[j] == "\\" else 1
            j += 1
            # glued suffix @lang / ^^datatype belongs to the same term
            m = re.match(r"@[A-Za-z][A-Za-z0-9-]*|\^\^[^\s;,.\])}]+", text[j:])
            yield "TERM"
            i = j + (m.end() if m else 0)
        elif c == "<":
            j = text.find(">", i)
            yield "TERM"
            i = (j + 1) if j != -1 else n
        elif c == "{":
            j = _scan_interpolation(text, i)
            m = re.match(r"@[A-Za-z][A-Za-z0-9-]*|\^\^[^\s;,.\])}]+", text[j:])
            yield "TERM"
            i = j + (m.end() if m else 0)
        elif c in "[]();,":
            yield c
            i += 1
        elif c == ".":
            yield "."
            i += 1
        else:
            m = re.match(r"[?$]?[A-Za-z_][\w·-]*(?:\.[\w·-]+)*(:[\w·.-]*)?"
                         r"|[+-]?\d[\w.]*|_:[\w.-]*", text[i:])
            if m:
                yield "TERM"
                i += m.end()
            else:
                i += 1


def count_triples(text: str) -> int:
    """Explicit predicate–object assertions in one g{...} island body:
    one triple per object term in predicate–object lists, recursively
    inside ``[ ... ]`` property lists; collection elements are not
    assertions (their first/rest expansion is counted by
    ``triples_semantic`` instead)."""
    toks = list(_turtle_tokens(text))
    pos = 0
    triples = 0

    def peek():
        return toks[pos] if pos < len(toks) else None

    def take():
        nonlocal pos
        t = toks[pos] if pos < len(toks) else None
        pos += 1
        return t

    def parse_term():
        nonlocal triples
        t = take()
        if t == "[":
            parse_po_list(closing="]")
        elif t == "(":
            while peek() not in (")", None):
                parse_term()
            take()   # ')'

    def parse_po_list(closing):
        nonlocal triples
        while peek() not in (closing, None, "."):
            # predicate
            if peek() == ";":
                take()
                continue
            parse_term()
            # objects
            if peek() in (closing, None, ".", ";"):
                continue   # dangling predicate: malformed, be lenient
            parse_term()
            triples += 1
            while peek() == ",":
                take()
                parse_term()
                triples += 1
            if peek() == ";":
                take()
        if peek() == closing:
            take()

    while peek() is not None:
        if peek() in (".", ";", ","):
            take()
            continue
        parse_term()          # subject
        parse_po_list(closing=None)
    return triples


def _top_level_statements(text: str) -> list[str]:
    """Split a g{} body on top-level '.' separators (bracket/string aware)."""
    parts, buf = [], []
    i, n, depth = 0, len(text), 0
    while i < n:
        c = text[i]
        if c in "\"'":
            q = c
            j = i + 1
            while j < n and text[j] != q:
                j += 2 if text[j] == "\\" else 1
            buf.append(text[i:j + 1])
            i = j + 1
            continue
        if c == "<":
            j = text.find(">", i)
            j = j if j != -1 else n - 1
            buf.append(text[i:j + 1])
            i = j + 1
            continue
        if c == "{":
            j = _scan_interpolation(text, i)
            buf.append(text[i:j])
            i = j
            continue
        if c in "[(":
            depth += 1
        elif c in "])":
            depth -= 1
        if c == "." and depth == 0 and (i + 1 == n or not text[i + 1].isalnum()):
            part = "".join(buf).strip()
            if part:
                parts.append(part)
            buf = []
            i += 1
            continue
        buf.append(c)
        i += 1
    part = "".join(buf).strip()
    if part:
        parts.append(part)
    return parts


# --- whole-source measurement ----------------------------------------------

@dataclass
class LdpyMeasure:
    loc: int = 0
    code_loc: int = 0
    chars: int = 0
    tokens: int = 0
    syntax_nodes: int = 0
    islands: int = 0
    island_kinds: dict = field(default_factory=dict)
    island_chars: int = 0
    terms: int = 0
    triples_expressed: int = 0
    triples_semantic: int = 0    # tuples in generated graph()/add_to() calls
    patterns_expressed: int = 0  # patterns of -{ } and m{ }
    patterns_semantic: int = 0   # tuples in generated remove_from()/match()
    scaffolding_tokens: int = 0
    term_depth_sum: int = 0
    python_tokens: int = 0       # tokens outside islands
    masked_source: str = ""      # islands replaced by placeholders (valid Python)

    def to_dict(self) -> dict:
        d = {k: v for k, v in self.__dict__.items() if k != "masked_source"}
        return d


# Runtime call -> how many tuples it carries, given its argument list.
# `graph(namespaces, base, *triples)`, `add_to(g, *triples)`,
# `remove_from(g, *patterns)`; `match(g, (patterns,), (vars,))` passes its
# patterns as one tuple literal.
_ASSERTING = {"graph": 2, "add_to": 1}
_MATCHING = {"remove_from": 1}


def _semantic_counts(generated_code: str) -> tuple[int, int]:
    """(triples asserted, patterns expressed) in the transpiled code.

    Reading the emitted runtime calls rather than the island text is what
    makes collection and blank-node expansion count: ``( 1 2 )`` is one
    written term and five emitted triples.
    """
    try:
        tree = ast.parse(generated_code)
    except SyntaxError:
        return 0, 0
    triples = patterns = 0
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "_ldpy_"):
            continue
        name = node.func.attr
        if name in _ASSERTING:
            triples += max(0, len(node.args) - _ASSERTING[name])
        elif name in _MATCHING:
            patterns += max(0, len(node.args) - _MATCHING[name])
        elif name == "match" and len(node.args) >= 2:
            arg = node.args[1]
            if isinstance(arg, (ast.Tuple, ast.List)):
                patterns += len(arg.elts)
    return triples, patterns


def _semantic_triples(generated_code: str) -> int:
    """Kept for callers that only want the assertion count."""
    return _semantic_counts(generated_code)[0]


def measure_ldpy_source(source: str) -> LdpyMeasure:
    r = _transpile(source)
    spans = island_spans(source)
    lines = source.splitlines()
    idx = _line_index(source)
    m = LdpyMeasure()
    m.loc = len(lines)
    m.chars = len(source)
    m.triples_semantic, m.patterns_semantic = _semantic_counts(r.code)

    # mask islands with placeholders, gather island texts
    masked = source
    stats = IslandStats()
    graph_bodies: list[str] = []      # islands that ASSERT triples
    pattern_bodies: list[str] = []    # islands that express PATTERNS
    offsets = []
    for k, (l0, c0, l1, c1, kind) in enumerate(spans):
        start, end = _offset(idx, l0, c0), _offset(idx, l1, c1)
        offsets.append((start, end, kind))
        m.island_kinds[kind] = m.island_kinds.get(kind, 0) + 1
        text = source[start:end]
        m.island_chars += len(text)
        if kind in ("island:graph", "island:g", "island:addto"):
            graph_bodies.append(text[text.find("{") + 1:text.rfind("}")])
        elif kind in ("island:removefrom", "island:match"):
            pattern_bodies.append(text[text.find("{") + 1:text.rfind("}")])
        tokenize_island(text, kind, stats)
        if kind.startswith("island:prefix") or kind.startswith("island:base"):
            stats.structures += 1
    m.islands = len(spans)
    # replace from the end to keep offsets valid
    for start, end, kind in sorted(offsets, reverse=True):
        start = _widen_over_modifier(masked, start, kind)
        masked = masked[:start] + _placeholder(kind) + masked[end:]
    m.masked_source = masked

    m.python_tokens = _python_tokens(masked) - m.islands  # placeholders out
    m.tokens = m.python_tokens + stats.tokens + stats.interp_py_tokens
    try:
        py_nodes = sum(1 for n in ast.walk(ast.parse(masked)) if hasattr(n, "lineno"))
    except SyntaxError as e:
        raise LdpyMetricsError(f"masked source unparsable: {e}") from e
    m.terms = stats.terms
    for body in graph_bodies:
        m.triples_expressed += count_triples(body)
    for body in pattern_bodies:
        m.patterns_expressed += count_triples(body)
    m.syntax_nodes = (py_nodes - m.islands            # placeholders removed
                      + stats.terms + m.triples_expressed
                      + m.patterns_expressed
                      + stats.structures + stats.interp_py_nodes)
    m.scaffolding_tokens = stats.tokens - stats.term_tokens
    m.term_depth_sum = stats.depth_sum

    # code_loc: non-blank, non-comment-only lines of the original source
    # (same convention as the OTTR study harness)
    m.code_loc = sum(1 for ln in lines
                     if ln.strip() and not ln.strip().startswith("#"))
    return m


def _is_expression_island(kind: str) -> bool:
    return not (kind.startswith("island:prefix") or kind.startswith("island:base"))


#: An island that is only PART of a statement cannot be masked by `pass`.
#: `for @bindings in` spans those three words and nothing else — the iterable
#: and the `:` stay Python — so `pass` there yields `pass (rows):`, which does
#: not parse, and the whole region loses its metrics. That silently hit the
#: one stratum whose target construction this is (`add_in_loop`).
_PARTIAL = {
    "island:for-bindings": "for __I__ in",
    "island:for-bindings-close": ":",
}


#: `global` and `nonlocal` widen the scope of a declaration island, and the
#: language map leaves them to Python — they ARE Python keywords, and that is
#: what the highlighters colour them as.  For masking, though, the modifier
#: and its island are one statement: replacing only the island leaves
#: `global pass`, which does not parse, and the whole region loses its
#: metrics.  That silently hit the one function in the corpus that declares
#: nineteen prefixes at once.
_MODIFIER_RE = re.compile(r"(?:global|nonlocal)[ \t]+$")


def _widen_over_modifier(text: str, start: int, kind: str) -> int:
    """Where the mask of a statement island really begins."""
    if _placeholder(kind) != "pass":
        return start
    line_start = text.rfind("\n", 0, start) + 1
    m = _MODIFIER_RE.search(text, line_start, start)
    return m.start() if m else start


def _placeholder(kind: str) -> str:
    """What stands in for an island so the rest still parses as Python."""
    if kind in _PARTIAL:
        return _PARTIAL[kind]
    return "__I__" if _is_expression_island(kind) else "pass"

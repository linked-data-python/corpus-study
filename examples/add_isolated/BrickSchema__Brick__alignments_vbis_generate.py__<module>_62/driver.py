"""Validation driver for BrickSchema__Brick__alignments_vbis_generate.py__<module>_62.

Module-level region (kind: statement, qualname <module>) with no entry
point: `original.py` and `translated.ldpy` are both executed top to bottom
and their module globals compared. The only rdflib Graph in scope is
`graph`, so the oracle is RDF isomorphism on it (meta.oracle ==
"isomorphism").

The region's own helpers (get_brick_class, get_vbis_tags,
rewrite_vbis_pattern) live ABOVE line 62 in the source file, outside this
extraction; the context shim vbis_context.py reproduces the three functions
verbatim so the `with open("vbis-brick-v5.csv") as f:` loop has something
to call. vbis-brick-v5.csv itself is not part of the source repository (the
real file has thousands of rows) -- it is a small fixture written for this
pair, covering: a class with a single VBIS pattern (SH:pattern branch), a
class with two patterns (SH:or + rdf:Collection branch), a class with two
fully-qualified tags (SH:in + rdf:Collection branch), a class with a single
fully-qualified tag (SH:hasValue branch), a repeated class (skipped via
`finished_brick_classes`, second occurrence must not add a second shape), a
row with no Brick Class column filled in (skipped, `bc is None`), and a
class with no VBIS tags at all (skipped, `len(tagsOrPatterns) == 0` -- the
neighbourhood that must not produce a shape).

Second run: the repository's prefix bindings.  In the repository the graph
is not bare when the region starts: generate.py lines 11-13 bind `brick`,
`sh` and `vbisalign` on it, and line 127, right after the region,
serialises it to Brick-VBIS-alignment.ttl -- so the prefix under which the
VBIS namespace is written is part of what the region decides.  The
extraction left those three lines out, so the first run cannot see what
`@graph graph` does to them.  This run executes both artefacts again, from
text, with the context line `graph = Graph()` followed by the repository's
three `graph.bind(...)` calls, and requires (a) the graphs to be isomorphic
again and (b) every binding of the original's graph to be present in the
translation's (`@graph` may ADD the block's prefixes, record ldpy/027, but
must not replace one the caller had set).  A `@prefix vbis:` on that IRI
rebinds it from `vbisalign` to `vbis` (rdflib's `bind` overrides by
default): this run reports it.
"""
import contextlib
import io
from pathlib import Path

from rdflib.compare import to_isomorphic

from rdfeval.harness import _emit, _redirected, run_pair

HERE = Path(__file__).resolve().parent

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  Its verdict is captured and
# re-emitted below, merged with the second run's differences.
with contextlib.redirect_stderr(io.StringIO()):
    VERDICT = run_pair(
        __file__,
        entry=None,
        calls=None,
    )

# generate.py lines 7 and 11-13 of BrickSchema/Brick@c12949f236.
CONTEXT_LINE = "graph = Graph()\n"
REPO_CONTEXT = (
    "graph = Graph()\n"
    'graph.bind("brick", "https://brickschema.org/schema/Brick#")\n'
    'graph.bind("sh", "http://www.w3.org/ns/shacl#")\n'
    'graph.bind("vbisalign", "https://brickschema.org/schema/Brick/alignments/vbis#")\n'
)


def _run_in_repo_context(path):
    """Execute one artefact with the repository's bindings set on `graph`."""
    path = _redirected(path)
    text = path.read_text()
    if text.count(CONTEXT_LINE) != 1:
        raise RuntimeError(f"{path.name}: context line {CONTEXT_LINE!r} not found once")
    text = text.replace(CONTEXT_LINE, REPO_CONTEXT)
    if path.suffix == ".ldpy":
        from ldpy.transpiler import transpile
        text = transpile(text, filename=str(path)).code
    ns = {"__name__": "__repo_context__", "__file__": str(path)}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(text, str(path), "exec"), ns)
    return ns["graph"]


if not VERDICT.get("error"):
    extra = []
    go = _run_in_repo_context(HERE / "original.py")
    gt = _run_in_repo_context(HERE / "translated.ldpy")
    if to_isomorphic(go) != to_isomorphic(gt):
        extra.append(f"repo context: graphs not isomorphic ({len(go)} vs {len(gt)} triples)")
    bo = {(p, str(u)) for p, u in go.namespaces()}
    bt = {(p, str(u)) for p, u in gt.namespaces()}
    lost = sorted(bo - bt)
    if lost:
        extra.append(f"repo context: prefix bindings of the original lost in the translation: {lost}")
    VERDICT["method"] += " + repo-context bindings"
    VERDICT["diffs"] = VERDICT["diffs"] + extra
    VERDICT["equivalent"] = not VERDICT["diffs"]

_emit(VERDICT)

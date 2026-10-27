"""Validation driver for mpsonntag__snippets__python_odml_examples_example_rdf_query.py__<module>_17.

The region only PREPARES a query (`q = prepareQuery(...)` / `q = s{ ... }`);
what the repository does with `q` is on the very next lines of the module
(example_rdf_query.py:25-26, repeated for the four other queries of the file):

    for row in graph.query(q):
        print("Doc: %s, Sec: %s" % (row.d, row.s))

so that is what this driver exercises, on a fixture graph, comparing exactly
what the repository reads (`row.d`, `row.s`) plus the projected variables of
`SELECT *`:

  * original.py: `graph.query(q)`, verbatim from the repository.
  * translated.ldpy: `q` is an ldpy PreparedQuery, not an rdflib Query, so
    `graph.query(q)` cannot be used (see PROBE below); the consumer is the
    rewritten call site `for row in q(graph)` -- the interface change that
    makes this pair `minor-restructuring`, not a hidden equivalence.

PROBE -- the driver also asserts the interface gap instead of masking it:
`graph.query(q_translated)` must raise `AttributeError: ... 'algebra'`. The
verdict records it under `interface_gap`; if the language ever lets
`graph.query(q)` accept an s{ } value, this probe fails and the
classification must be revisited.

Fixture (fixture.ttl): two matching sections; neighbours that must NOT match
(wrong hasType, a case-different hasType, a parent that is not a Document, a
child that is not typed Section) and a document with no matching section.
"""
import sys
import traceback
from pathlib import Path

from rdfeval.harness import (_emit, _exec_ldpy, _exec_python, fixture_graph,
                              materialise)

EX_DIR = Path(__file__).resolve().parent
FIXTURE = EX_DIR / "fixture.ttl"


def _rows(execfn, filename):
    """(the (row.d, row.s) pairs the repository reads, projected variables)."""
    ns, _out = execfn(EX_DIR / filename)
    q = ns["q"]
    g = fixture_graph(FIXTURE)
    if hasattr(q, "graph"):
        # ldpy PreparedQuery: the call suffix q(g) binds it to a graph.
        result = q(g).execute()
    else:
        # rdflib Query from prepareQuery(): the repository's own call.
        result = g.query(q)
    pairs = [(row.d, row.s) for row in result]
    return pairs, sorted(str(v) for v in result.vars)


def _probe_graph_query(filename):
    """What `graph.query(q)` does with the artefact's q: ('ok'|'AttributeError: ...')."""
    ns, _out = _exec_ldpy(EX_DIR / filename)
    try:
        fixture_graph(FIXTURE).query(ns["q"])
    except AttributeError as e:
        return f"AttributeError: {e}"
    return "ok"


verdict = {"example": EX_DIR.name, "equivalent": False,
           "method": "custom:query-fixture", "diffs": [], "error": None}
try:
    rows_original = _rows(_exec_python, "original.py")
    rows_translated = _rows(_exec_ldpy, "translated.ldpy")
    probe = _probe_graph_query("translated.ldpy")
except Exception:
    verdict["error"] = traceback.format_exc(limit=8)
    _emit(verdict)
    sys.exit(0)

# No store promises an order; compare as multisets.
key = lambda rows: sorted((tuple(map(repr, row)) for row in rows))
diffs = []
if key(rows_original[0]) != key(rows_translated[0]):
    diffs.append(f"query results differ: {rows_original[0]!r} vs {rows_translated[0]!r}")
if rows_original[1] != rows_translated[1]:
    diffs.append(f"projected variables differ: {rows_original[1]!r} vs {rows_translated[1]!r}")
if len(rows_original[0]) != 2:
    diffs.append(f"fixture should yield exactly 2 solutions, got {len(rows_original[0])}")
if not probe.startswith("AttributeError") or "algebra" not in probe:
    diffs.append(f"interface-gap probe changed: graph.query(q) on the s{{ }} value gave {probe!r}")
verdict["interface_gap"] = probe
verdict["diffs"] = diffs
verdict["equivalent"] = not diffs
VERDICT = verdict
_emit(verdict)

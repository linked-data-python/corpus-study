"""Validation driver for mpsonntag__snippets__python_odml_examples_example_rdf_query.py__<module>_17.

The region only PREPARES a query (`q = prepareQuery(...)` / `q = s{ ... }`);
it is never executed where it is written. Comparing the two `q` objects
themselves is not meaningful (rdflib's prepared Query has no useful
`__eq__`, and an ldpy lazy query is a different wrapper type entirely), so
the oracle actually exercises what a prepared query is for: run each `q`
against the same fixture graph and compare the solutions -- the reading
oracle (design record corpus/405), applied one level removed from the
region's own top-level statements.
"""
import sys
import traceback
from pathlib import Path

from rdfeval.harness import (_emit, _exec_ldpy, _exec_python, fixture_graph,
                              materialise)

EX_DIR = Path(__file__).resolve().parent
FIXTURE = EX_DIR / "fixture.ttl"


def _rows(execfn, filename):
    ns, _out = execfn(EX_DIR / filename)
    q = ns["q"]
    g = fixture_graph(FIXTURE)
    # original.py's q is an rdflib prepareQuery() result: run with graph.query(q).
    # translated.ldpy's q is an ldpy PreparedQuery: the call suffix q(g) binds
    # it to a graph and makes it iterable (ldpy/runtime.py, PreparedQuery).
    result = q(g) if hasattr(q, "graph") else g.query(q)
    return materialise(result)


verdict = {"example": EX_DIR.name, "equivalent": False,
           "method": "custom:query-fixture", "diffs": [], "error": None}
try:
    rows_original = _rows(_exec_python, "original.py")
    rows_translated = _rows(_exec_ldpy, "translated.ldpy")
except Exception:
    verdict["error"] = traceback.format_exc(limit=8)
    _emit(verdict)
    sys.exit(0)

# No store promises an order; compare as multisets.
key = lambda rows: sorted((tuple(map(repr, row)) for row in rows))
diffs = []
if key(rows_original) != key(rows_translated):
    diffs.append(f"query results differ: {rows_original!r} vs {rows_translated!r}")
verdict["diffs"] = diffs
verdict["equivalent"] = not diffs
VERDICT = verdict
_emit(verdict)

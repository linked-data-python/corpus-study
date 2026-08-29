"""Validation driver for ktbs__ktbs__lib_ktbs_engine_obsel.py__<module>_328.

The region is a bare module-level statement --
`_RELATED_OBSELS = prepareQuery(...)` -- with no `graph` parameter and no
enclosing function, so neither of run_pair's built-in modes applies as-is:
module-state comparison only looks at rdflib Graphs and JSON-ish values (a
prepared query is neither -- see rdfeval.harness._comparable), and there is
no function to name as `entry`.

The oracle is built by hand instead, reusing the harness's own execution and
comparison helpers: run both modules, pull the prepared query out of each
namespace (`_RELATED_OBSELS`), execute it against the same small fixture
graph with the same `$obs` binding -- original.py via
`graph.query(q, initBindings=...)`, translated.ldpy via the island's own
call suffix (`s{ }(g, bindings)`, which is an ordinary call on the value the
island produced -- see bindings.md#the-call-suffix-explicit-context) -- and
compare the solutions as multisets (no store promises an order).

Two calls against one fixture graph: (1) obs=o1, related to o2 (`$obs ?pred
?other`) and o3 (`?other ?pred $obs`), both sharing o1's trace t1 -- proves
the UNION (both relation directions) and the `{KTBS.hasTrace}` interpolation
(used at both occurrences, exercising term-position interpolation twice)
are both honoured; o1 is also linked to o4, which has a DIFFERENT trace and
must NOT come back, so the trace filter is genuinely exercised and not just
"no predicate link". (2) obs=o5: shares the trace but has no predicate link
to anything -- the zero-solution case.
"""
import traceback
from pathlib import Path

from rdflib import Graph, URIRef

from obsel_context import KTBS
from rdfeval.harness import _exec_python, _exec_ldpy, materialise, _unordered, _emit

EX = "http://example.org/"
EX_DIR = Path(__file__).resolve().parent


def _fixture() -> Graph:
    g = Graph()
    o1, o2, o3, o4, o5 = (URIRef(EX + n) for n in ("o1", "o2", "o3", "o4", "o5"))
    t1, t2 = URIRef(EX + "t1"), URIRef(EX + "t2")
    precedes = URIRef(EX + "precedes")
    g.add((o1, KTBS.hasTrace, t1))
    g.add((o2, KTBS.hasTrace, t1))
    g.add((o3, KTBS.hasTrace, t1))
    g.add((o4, KTBS.hasTrace, t2))   # neighbour: related, but wrong trace
    g.add((o5, KTBS.hasTrace, t1))   # neighbour: right trace, no relation
    g.add((o1, precedes, o2))        # $obs ?pred ?other
    g.add((o3, precedes, o1))        # ?other ?pred $obs
    g.add((o1, precedes, o4))        # must NOT match: o4's trace differs
    return g, o1, o5


def _run_original(ns, obs):
    g, _, _ = _fixture()
    q = ns["_RELATED_OBSELS"]
    return materialise(list(g.query(q, initBindings={"obs": obs})))


def _run_translated(ns, obs):
    g, _, _ = _fixture()
    q = ns["_RELATED_OBSELS"]
    return materialise(list(q(g, {"obs": obs})))


verdict = {"example": EX_DIR.name, "equivalent": False,
           "method": "custom:prepared-query-execution", "diffs": [],
           "error": None}
try:
    ns_o, out_o = _exec_python(EX_DIR / "original.py")
    ns_t, out_t = _exec_ldpy(EX_DIR / "translated.ldpy")
    _, o1, o5 = _fixture()

    for label, obs in (("obs=o1 (two related, one wrong-trace neighbour)", o1),
                        ("obs=o5 (zero solutions)", o5)):
        ro = _run_original(ns_o, obs)
        rt = _run_translated(ns_t, obs)
        if _unordered(ro) != _unordered(rt):
            verdict["diffs"].append(f"{label}: solutions differ ({ro!r} vs {rt!r})")
except Exception:
    verdict["error"] = traceback.format_exc(limit=8)

verdict["equivalent"] = not verdict["diffs"] and verdict["error"] is None
_emit(verdict)
VERDICT = verdict

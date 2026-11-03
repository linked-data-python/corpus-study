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

Repair of 2026-10-30 -- the fixture now also holds, each with a call or a
row of the first call that it decides:

- o1 is linked to o2 by TWO predicates (`precedes`, `relatedTo`): without
  DISTINCT, (o2, o1) comes back twice -- the only place DISTINCT acts;
- o1 has a second property towards t2 (`alsoIn`): a neighbour of `$obs
  {KTBS.hasTrace} ?trace` sharing its subject and object.  If that
  occurrence were widened to a variable, o4 (related to o1, trace t2) would
  come back;
- o6 is related to o1 and carries t1 through `alsoIn`, but its trace is t3:
  the neighbour of `?other {KTBS.hasTrace} ?trace`.  If that occurrence were
  widened to a variable, o6 would come back;
- a blank-node obsel `_:b1` (trace t1, preceded by o2), queried as `$obs`:
  `get_obsel_bounded_description` documents its `node` as "uri or blank",
  so the binding is exercised with a BNode as well as with an URIRef.

What the driver does NOT reproduce: the repository consumes the value
outside the region, at lib/ktbs/engine/obsel.py:323, as
`graph.query(_RELATED_OBSELS, initBindings={"obs": node})`.  The value of
`s{ }` does not go through `graph.query` (rdflib raises AttributeError:
'PreparedQuery' object has no attribute 'algebra'); the translated side is
therefore run through the island's call suffix, i.e. with that call site
rewritten.  Whether that rewrite outside the region is acceptable is a
classification question left to the human review (see meta.json "repair").
"""
import traceback
from pathlib import Path

from rdflib import BNode, Graph, URIRef

from obsel_context import KTBS
from rdfeval.harness import (_exec_python, _exec_ldpy, materialise, _unordered,
                             _emit, sides_from_env)

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
    # repair of 2026-10-30 (see the docstring)
    o6, b1 = URIRef(EX + "o6"), BNode("b1")
    t3 = URIRef(EX + "t3")
    related, also_in = URIRef(EX + "relatedTo"), URIRef(EX + "alsoIn")
    g.add((o1, related, o2))         # second link o1-o2: DISTINCT acts
    g.add((o1, also_in, t2))         # neighbour of $obs hasTrace ?trace
    g.add((o1, precedes, o6))        # o6: related to o1 ...
    g.add((o6, also_in, t1))         # ... t1 through another predicate ...
    g.add((o6, KTBS.hasTrace, t3))   # ... but its trace is t3: must NOT match
    g.add((b1, KTBS.hasTrace, t1))   # a blank-node obsel
    g.add((o2, precedes, b1))
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
    # an optimized Python artefact holds a prepared query, run as the
    # original is; an island's value is run through its call suffix
    run_right = (_run_original if sides_from_env()[1].endswith(".py")
                 else _run_translated)

    for label, obs in (("obs=o1 (two related, one wrong-trace neighbour)", o1),
                        ("obs=o5 (zero solutions)", o5),
                        ("obs=_:b1 (a blank-node obsel)", BNode("b1"))):
        ro = _run_original(ns_o, obs)
        rt = run_right(ns_t, obs)
        if _unordered(ro) != _unordered(rt):
            verdict["diffs"].append(f"{label}: solutions differ ({ro!r} vs {rt!r})")
except Exception:
    verdict["error"] = traceback.format_exc(limit=8)

verdict["equivalent"] = not verdict["diffs"] and verdict["error"] is None
_emit(verdict)
VERDICT = verdict

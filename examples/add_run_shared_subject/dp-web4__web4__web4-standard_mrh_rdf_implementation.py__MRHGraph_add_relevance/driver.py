"""Validation driver for
dp-web4__web4__web4-standard_mrh_rdf_implementation.py__MRHGraph_add_relevance.

`add_relevance` is a bare method (extracted without its enclosing MRHGraph
class): it reads/writes `self.graph` and `self.edges`, neither visible in
the extracted region. `context_shim.MRHGraphStub` restores those bindings
(see its docstring and meta.json).

Two fixtures:
  - an edge WITH `conditional_on` (two conditions), to exercise the `if` /
    `for` loop that adds one `mrh:conditional_on` triple per condition --
    the branch a single edge without conditions never reaches;
  - an edge with `conditional_on=None`, the common case, which must add
    none of those triples and must not error on the falsy check.

Both exercise the four fused `+{ }` groups: the lone type triple (separated
from the target/probability group by the intervening `target_uri =`
computation), the target+probability pair, and the relation+distance+decay
triple (separated from the previous pair by the intervening `rel_uri =`
computation) -- see meta.json for why the boundaries fall exactly there.
"""
from rdfeval.harness import run_pair
from context_shim import MRHEdge, MRHRelation

EDGE_WITH_CONDITIONS = MRHEdge(
    target_lct="lct:web4:edge-device-42",
    probability=0.82,
    relation=MRHRelation.DEPENDS_ON,
    distance=2,
    decay_rate=0.75,
    conditional_on=["lct:web4:condition-a", "lct:web4:condition-b"],
)

EDGE_WITHOUT_CONDITIONS = MRHEdge(
    target_lct="lct:web4:sensor-7",
    probability=1.0,
    relation=MRHRelation.WITNESSING,
    # distance and decay_rate left at their dataclass defaults (1, 0.9)
)

VERDICT = run_pair(
    __file__,
    entry="demo",
    calls=[
        ((EDGE_WITH_CONDITIONS,), {}),
        ((EDGE_WITHOUT_CONDITIONS,), {}),
    ],
)

"""Validation driver for IndustryFusion__DigitalTwin__semantic-model_opcua_lib_utils.py__RdfUtils_get_all_subreferences.

`get_all_subreferences` reads a graph -- the reading oracle applies (design
record corpus/405) -- but it needs an object with an `.opcuans` attribute as
`self` (used only by the query's `initNs`, itself unused by the query text:
see meta.json), which a bare `fixture="fixture.ttl"` graph argument cannot
express.  So the fixture is built here, in Python, through `calls=`, exactly
with the same care as a `fixture.ttl` would need: several solutions, the
zero-solution case, and neighbouring triples that must not match.

No store promises an order over query solutions, and the region does not
sort its own result (unlike OpenEnergyPlatform__oeplatform__factsheet_helper
in this same lot), so `ordered=False`.
"""
from types import SimpleNamespace

from rdflib import Graph, Namespace, RDFS
from rdfeval.harness import run_pair

EX = Namespace("http://example.org/")


def _rdfutils_stub():
    """Stand-in for RdfUtils: only the `.opcuans` attribute that the query's
    (unused) initNs reads is needed to match the call signature.  A fresh
    `SimpleNamespace` per call (so the two sides never share an instance)
    that still compares equal by attribute value, so run_pair's own arg
    comparison does not report a spurious diff on object identity."""
    return SimpleNamespace(opcuans=Namespace("http://example.org/opcua/"))


def _graph_with_matches():
    g = Graph()
    g.bind("ex", EX)
    # node1 --p1--> target1, and p1 is a direct rdfs:subPropertyOf super:
    # matches (reference=ex:p1, target=ex:target1) -- one path hop.
    g.add((EX.node1, EX.p1, EX.target1))
    g.add((EX.p1, RDFS.subPropertyOf, EX.super))
    # node1 --super--> target2 directly: matches (reference=ex:super,
    # target=ex:target2) via the zero-length leg of subPropertyOf*.
    g.add((EX.node1, EX.super, EX.target2))
    # neighbourhood: p2 is NOT a subproperty of super -> must not match.
    g.add((EX.node1, EX.p2, EX.target3))
    # neighbourhood: same predicate p1, but from a different node -> must
    # not match (?node is bound to node1 in the call below).
    g.add((EX.other, EX.p1, EX.target4))
    return g


def _call_with_matches():
    return (_rdfutils_stub(), _graph_with_matches(), EX.node1, EX.super), {}


def _call_zero_solutions():
    # ex:zzz has no outgoing triples at all in this graph: the
    # zero-solution case.
    return (_rdfutils_stub(), _graph_with_matches(), EX.zzz, EX.super), {}


VERDICT = run_pair(
    __file__,
    entry='get_all_subreferences',
    calls=[_call_with_matches, _call_zero_solutions],
    ordered=False,
)

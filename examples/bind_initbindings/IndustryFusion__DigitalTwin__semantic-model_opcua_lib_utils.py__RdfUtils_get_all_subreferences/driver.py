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

Mutation audit of 2026-10-30.  The first two calls only exercise a path of
length 0 and 1, so `subPropertyOf*` -> `subPropertyOf?` stayed green.  The
third call (`_call_deep_hierarchy`) reads a hierarchy shaped like the
OPC UA one the repository walks (owl2instances.py:262-268 asks for
HasChild, Organizes and NonHierarchicalReferences, whose subproperties are
two and more levels down):

  * a chain of two and three hops (q -> p1 -> super, r -> q -> p1 -> super):
    kills `?`;
  * a diamond (d -> a, d -> b, a -> super, b -> super): rdflib's `*` path
    yields `d` once, so the row (d, target) must appear once on both sides;
  * a reflexive subproperty (c -> c -> super) and a cycle (x -> y -> x),
    the cycle NOT reaching super: must not match;
  * a literal and a blank node as targets of a matching reference;
  * the start node itself used as a target from another subject, and as
    a subject of an rdfs:subPropertyOf triple: neither may surface.
"""
from types import SimpleNamespace

from rdflib import BNode, Graph, Literal, Namespace, RDFS
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


def _graph_deep_hierarchy():
    g = Graph()
    g.bind("ex", EX)
    sub = RDFS.subPropertyOf
    # two and three hops
    g.add((EX.p1, sub, EX.super))
    g.add((EX.q, sub, EX.p1))
    g.add((EX.r, sub, EX.q))
    g.add((EX.node1, EX.q, EX.t_q))
    g.add((EX.node1, EX.r, EX.t_r))
    # diamond
    g.add((EX.d, sub, EX.a))
    g.add((EX.d, sub, EX.b))
    g.add((EX.a, sub, EX.super))
    g.add((EX.b, sub, EX.super))
    g.add((EX.node1, EX.d, EX.t_d))
    # reflexive subproperty, and a cycle that never reaches super
    g.add((EX.c, sub, EX.c))
    g.add((EX.c, sub, EX.super))
    g.add((EX.node1, EX.c, EX.t_c))
    g.add((EX.x, sub, EX.y))
    g.add((EX.y, sub, EX.x))
    g.add((EX.node1, EX.x, EX.t_x))
    # a literal and a blank node as targets
    g.add((EX.node1, EX.p1, Literal("")))
    g.add((EX.node1, EX.p1, BNode("b1")))
    # node1 as object, and as subject of a subPropertyOf triple
    g.add((EX.other, EX.p1, EX.node1))
    g.add((EX.node1, sub, EX.super))
    return g


def _call_deep_hierarchy():
    return (_rdfutils_stub(), _graph_deep_hierarchy(), EX.node1, EX.super), {}


VERDICT = run_pair(
    __file__,
    entry='get_all_subreferences',
    calls=[_call_with_matches, _call_zero_solutions, _call_deep_hierarchy],
    ordered=False,
)

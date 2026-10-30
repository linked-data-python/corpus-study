"""Validation driver for dtai-kg__SCOOP__SCOOP_shape_adjustment_single.py__ShapeAdjustment_double_check.

This region READS a graph and prunes it, so the oracle is not the isomorphism
of a graph both versions build but the equality of what they produce from the
same input graph (design record corpus/405).  `fixture.ttl` is parsed fresh for
each side; `Probe` below carries it in as the `self` the method walks, together
with the list of adjusted identifiers the method iterates.

double_check returns nothing: what it produces is the pruned graph, so the
comparison is the isomorphism of `self.adjusted_graph` (plus the identifier
list, which must come out untouched).  It is spelled as an `__eq__` on the
context object because `harness.materialise` cannot walk one on its own.

The calls:
  adjusted_shapes    - fixture.ttl: two node shapes stripped of most of the
                       thirteen constraints, a property shape the "NodeShape"
                       test skips, an identifier with no triple (zero
                       solutions), a node shape that is not adjusted;
  nothing_adjusted   - the empty identifier list: nothing is walked;
  neighbours         - fixture_neighbours.ttl (repair 2026-10-30): every
                       removed triple has a twin sharing two of its three
                       terms - same subject and object under a predicate
                       outside the list (kills a removal whose predicate is
                       widened to ?q), same predicate and object under a
                       subject that is not adjusted, the identifier as an
                       object - plus several objects for one predicate,
                       nested blank nodes, falsy objects (0, "") and a shape
                       every triple of which is removed while it is walked.
                       The identifier list carries a duplicate and a
                       non-NodeShape IRI, and the order walks the fully
                       removed shape first.
"""
from pathlib import Path

from rdflib import URIRef

from rdfeval.harness import fixture_graph, graphs_isomorphic, run_pair
from scoop_context import ShapeAdjustment

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"

# What reassign_identifier() leaves in self.adjusted_identifier: two node
# shapes of the fixture, one that carries no triple at all (zero solutions),
# and one property shape, which the "NodeShape" test skips.
ADJUSTED = [
    URIRef("http://example.com/NodeShape/Person"),
    URIRef("http://example.com/PropertyShape/name1234"),
    URIRef("http://example.com/NodeShape/Absent"),
    URIRef("http://example.com/NodeShape/Address"),
]


class Probe(ShapeAdjustment):
    """The context object of the region, made comparable."""

    def __eq__(self, other):
        return (graphs_isomorphic(self.adjusted_graph, other.adjusted_graph)
                and self.adjusted_identifier == other.adjusted_identifier)


def adjusted_shapes():
    return ((Probe(fixture_graph(FIXTURE), list(ADJUSTED)),), {})


def nothing_adjusted():
    return ((Probe(fixture_graph(FIXTURE), []),), {})


NEIGHBOURS = HERE / "fixture_neighbours.ttl"
ADJUSTED_NEIGHBOURS = [
    URIRef("http://example.com/shapes/PersonNodeShape"),
    URIRef("http://example.com/NodeShape/Wide"),
    URIRef("http://example.com/Referrer"),
    URIRef("http://example.com/NodeShape/Wide"),
]


def neighbours():
    return ((Probe(fixture_graph(NEIGHBOURS), list(ADJUSTED_NEIGHBOURS)),), {})


VERDICT = run_pair(
    __file__,
    entry='double_check',
    fixture="fixture.ttl",
    calls=[adjusted_shapes, nothing_adjusted, neighbours],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)

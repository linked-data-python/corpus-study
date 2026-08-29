"""Validation driver for dtai-kg__SCOOP__SCOOP_shape_adjustment_single.py__ShapeAdjustment_findNode.

This region READS a graph and prunes it, so the oracle is not the isomorphism
of a graph both versions build but the equality of what they produce from the
same input graph (design record corpus/405).  `fixture.ttl` is parsed fresh for
each side; `Probe` below carries it in as the `self` whose graph the method
walks.

findNode returns nothing: what it produces is (a) the pruned graph and (b) the
list of shapes it collects, so the comparison covers both.  It is spelled as an
`__eq__` on the context object because `harness.materialise` cannot walk an
rdflib Resource or a class on its own.  The two calls exercise a shape with
children (and a child of a child: the region recurses) and a shape with none,
which is the zero-solution case.
"""
import sys
from pathlib import Path

from rdflib import URIRef

from rdfeval.harness import fixture_graph, graphs_isomorphic, run_pair
from scoop_context import ShapeAdjustment

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"
ROOT = URIRef("http://example.com/NodeShape/Person")
LEAF = URIRef("http://example.com/NodeShape/Employer")


class Probe(ShapeAdjustment):
    """The context object of the region, made comparable and re-entrant."""

    def findNode(self, node):
        # The region recurses through `self`.  Dispatch back into whichever
        # module is running — original.py or translated.ldpy — by reading the
        # region's own globals off the calling frame.
        return sys._getframe(1).f_globals["findNode"](self, node)

    def __eq__(self, other):
        return (graphs_isomorphic(self.initial_graph, other.initial_graph)
                and sorted(map(str, self.adjusted_shape))
                == sorted(map(str, other.adjusted_shape)))


def walk_from_root():
    return ((Probe(fixture_graph(FIXTURE)), ROOT), {})


def walk_from_leaf():
    return ((Probe(fixture_graph(FIXTURE)), LEAF), {})


VERDICT = run_pair(
    __file__,
    entry='findNode',
    fixture="fixture.ttl",
    calls=[walk_from_root, walk_from_leaf],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)

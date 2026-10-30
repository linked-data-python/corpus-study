"""Validation driver for mathiasrichter__shapiro__shapiro_model.py__ShaclProperty_get_nodeshapes.

Establishes semantic equivalence of original.py and translated.ldpy.

get_nodeshapes reads a graph reachable through ``self.graph`` and returns a
value (a sorted list of NodeShape), so this is a reading region: the oracle
is equality of what both versions produce from the same input graph
(fixture.ttl), not graph isomorphism. The entry point takes ``self`` rather
than a graph, so a fake ``self`` is built per call from the fixture instead
of using ``fixture=`` directly.

Calls:

* prop1: two matching shapes (labels already in alphabetical order), with
  neighbouring data (Shape3, on otherProp) that must not match;
* prop2: zero solutions;
* otherProp: exactly one matching shape;
* prop3: two matching shapes whose labels ("Zeta", "Alpha") sort in the
  opposite order to their storage order and to their IRIs, so
  ``shapes.sort(key=lambda s: s.label)`` changes the result;
* "bn1": an identifier WITHOUT scheme, i.e. the blank-node branch
  (``BNode(self.iri)``). Turtle renames the blank nodes it parses, so the
  driver adds the triple ``ex:Shape4 sh:property _:bn1`` to the fixture graph
  by hand; ``URIRef("bn1")`` would not match it. This is the common case in
  real SHACL, where ``sh:property`` objects are almost always blank nodes;
* "bn2": a second blank node held by two shapes labelled "Zeta" / "Alpha", so
  the sort is also exercised on the BNode branch.
"""
from pathlib import Path

from rdflib import BNode, Literal, Namespace, RDFS

from rdfeval.harness import fixture_graph, run_pair
from shim import SHAPE_QUERY

FIXTURE = "fixture.ttl"
EX = Namespace("http://example.org/")
SH = Namespace("http://www.w3.org/ns/shacl#")


def _add_blank_node_cases(graph):
    """Shapes pointing at blank nodes, whose ids the Turtle parser would rename."""
    graph.add((EX.Shape4, SH.property, BNode("bn1")))
    graph.add((EX.Shape4, RDFS.label, Literal("Shape Four")))
    graph.add((EX.ShapeC, SH.property, BNode("bn2")))
    graph.add((EX.ShapeC, RDFS.label, Literal("Zeta")))
    graph.add((EX.ShapeD, SH.property, BNode("bn2")))
    graph.add((EX.ShapeD, RDFS.label, Literal("Alpha")))


class _FakeProperty:
    """Stand-in for a ShaclProperty instance: only .iri, .graph, .SHAPE_QUERY
    are read by the region. Compared by .iri only -- the fresh fixture graph
    parsed for each side gets its own blank-node-derived identifier, which is
    not part of what the region is expected to preserve."""

    def __init__(self, iri, graph, shape_query):
        self.iri = iri
        self.graph = graph
        self.SHAPE_QUERY = shape_query

    def __eq__(self, other):
        return isinstance(other, _FakeProperty) and self.iri == other.iri

    def __repr__(self):
        return f"_FakeProperty({self.iri!r})"


def _case(iri):
    def make():
        graph = fixture_graph(Path(__file__).parent / FIXTURE)
        _add_blank_node_cases(graph)
        return (_FakeProperty(iri, graph, SHAPE_QUERY),), {}
    return make


VERDICT = run_pair(
    __file__,
    entry="get_nodeshapes",
    calls=[
        _case("http://example.org/prop1"),  # two matching shapes
        _case("http://example.org/prop2"),  # zero solutions
        _case("http://example.org/otherProp"),  # exactly one matching shape
        _case("http://example.org/prop3"),  # two shapes, sort order != storage order
        _case("bn1"),  # blank-node branch (no scheme), one shape
        _case("bn2"),  # blank-node branch, two shapes, sort order != storage order
    ],
    ordered=True,  # the region itself sorts by label
)

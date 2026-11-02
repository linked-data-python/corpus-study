"""Validation driver for SHACLOntoConverter._convert_ontology_owl_restriction.

The region reads an ontology graph (self.onto_graph) with two queries, the
second one bound by initBindings on the ?c and ?p of the first, and it WRITES
the SHACL it derives into self._g (a kgtk Graph wrapping an rdflib Graph) and
self._class_nodes. Oracle: the region is called on a fresh converter whose
onto_graph is the fixture, and what it leaves in `self` (the derived graph,
isomorphism; the class-node table) is compared.

The fixture (fixture.ttl) holds: an exact cardinality; a falsy minCardinality
0 (so no sh:minCount) next to a max; two ranges on one restriction (sh:or);
equivalentClass with owl:hasValue; the same property with another range on
another class (ranges must be looked up per class and property); a
restriction without range or cardinality; and neighbours that must not match
(onProperty without owl:Restriction, an orphan restriction, a bare
cardinality on a class).

Second call: an ontology without any restriction (nothing derived).
"""
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import fixture_graph, run_pair
from shim import SHACLOntoConverter

FIXTURE = Path(__file__).parent / "fixture.ttl"


def _converter(onto_graph):
    c = SHACLOntoConverter()
    c.onto_graph = onto_graph
    return (c,), {}


def full():
    return _converter(fixture_graph(FIXTURE))


def empty():
    g = Graph()
    g.parse(data="<http://example.org/a> <http://example.org/p> 1 .",
            format="turtle")
    return _converter(g)


VERDICT = run_pair(
    __file__,
    entry="_convert_ontology_owl_restriction",
    calls=[full, empty],
    ordered=True,
)

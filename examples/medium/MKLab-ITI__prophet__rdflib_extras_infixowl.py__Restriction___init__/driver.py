"""Validation driver for Restriction.__init__.

The region is infixowl's ``Restriction.__init__`` lifted out of its class,
so it still calls ``super(Restriction, self).__init__`` and needs a real
``Restriction`` instance as ``self``.  ``Probe`` is a ``Restriction``
subclass with an inert constructor and an equality that includes graph
isomorphism, so the harness can compare the mutated ``self``.

The fixtures always pass an explicit ``graph`` (the region's ``graph=Graph()``
default is a shared mutable default; leaving it implicit would compare two
different accumulating graphs).
"""
from rdflib import BNode, Graph, Literal, URIRef

from rdfeval.harness import run_pair, graphs_isomorphic

from infixowl_context import OWL_NS, Class, Restriction

EX = "http://example.org/"
RDF_TYPE = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")


class Probe(Restriction):
    """A Restriction whose own constructor does nothing."""

    def __init__(self):  # noqa: D107 - deliberately inert
        pass

    def __eq__(self, other):
        return (self.identifier == other.identifier
                and self.restrictionType == other.restrictionType
                and self.restrictionRange == other.restrictionRange
                and graphs_isomorphic(self.graph, other.graph))

    def __repr__(self):
        return (f"Probe({self.identifier!r}, {self.restrictionType!r}, "
                f"{self.restrictionRange!r})")


def case_some_values_from():
    return ((Probe(), URIRef(EX + "p")),
            {"graph": Graph(), "someValuesFrom": URIRef(EX + "C"),
             "identifier": BNode("r")})


def case_class_range():
    g = Graph()
    return ((Probe(), URIRef(EX + "p")),
            {"graph": g, "allValuesFrom": Class(URIRef(EX + "C"), graph=g),
             "identifier": BNode("r")})


def case_cardinality():
    return ((Probe(), URIRef(EX + "p")),
            {"graph": Graph(), "maxCardinality": Literal(1),
             "identifier": BNode("r")})


def case_range_from_graph():
    # restrictionRange is neither Identifier nor Class -> read back from the
    # graph (the `else` branch)
    g = Graph()
    g.add((BNode("r"), OWL_NS.hasValue, Literal(7)))
    return ((Probe(), URIRef(EX + "p")),
            {"graph": g, "value": 7, "identifier": BNode("r")})


def case_already_populated():
    g = Graph()
    g.add((BNode("r"), OWL_NS.onProperty, URIRef(EX + "p")))
    g.add((BNode("r"), RDF_TYPE, OWL_NS.Restriction))
    g.add((BNode("r"), RDF_TYPE, OWL_NS.Class))
    g.add((BNode("r"), OWL_NS.someValuesFrom, URIRef(EX + "C")))
    return ((Probe(), URIRef(EX + "p")),
            {"graph": g, "someValuesFrom": URIRef(EX + "C"),
             "identifier": BNode("r")})


def case_owl_class_removed():
    # rdf:type owl:Class present but rdf:type owl:Restriction absent -> the
    # trailing graph.remove(...) actually removes something
    g = Graph()
    g.add((BNode("r"), RDF_TYPE, OWL_NS.Class))
    return ((Probe(), URIRef(EX + "p")),
            {"graph": g, "someValuesFrom": URIRef(EX + "C"),
             "identifier": BNode("r")})


VERDICT = run_pair(__file__, entry="__init__",
                   calls=[case_some_values_from, case_class_range,
                          case_cardinality, case_range_from_graph,
                          case_already_populated, case_owl_class_removed])

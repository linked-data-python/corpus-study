"""Validation driver: Class.isPrimitive(self) only reads through `self`.

The region was extracted out of its class, so the driver supplies a minimal
stand-in exposing exactly the four attributes the method touches
(identifier, graph, equivalentClass, complementOf).  The same stub is built
fresh for each side, so a mutation of the graph would show up in arg[0].
"""
from rdflib import BNode, Graph, Namespace, RDF, URIRef
from rdflib.collection import Collection
from rdflib.compare import to_isomorphic

from rdfeval.harness import run_pair

OWL = Namespace("http://www.w3.org/2002/07/owl#")
EX = Namespace("http://example.org/")


class StubClass:
    """Stand-in for infixowl.Class: what isPrimitive reads off `self`."""

    def __init__(self, identifier, graph, equivalentClass=(),
                 complementOf=None):
        self.identifier = identifier
        self.graph = graph
        self.equivalentClass = list(equivalentClass)
        self.complementOf = complementOf

    def __eq__(self, other):
        return (self.identifier == other.identifier
                and self.equivalentClass == other.equivalentClass
                and self.complementOf == other.complementOf
                and to_isomorphic(self.graph) == to_isomorphic(other.graph))


def plain_named_class():
    g = Graph()
    g.add((EX.C, RDF.type, OWL.Class))
    return ((StubClass(EX.C, g),), {})


def restriction():
    g = Graph()
    r = BNode("restriction")  # stable id: the fixture is built once per side
    g.add((r, RDF.type, OWL.Restriction))
    g.add((r, OWL.onProperty, EX.p))
    return ((StubClass(r, g),), {})


def with_equivalent_class():
    g = Graph()
    g.add((EX.C, RDF.type, OWL.Class))
    return ((StubClass(EX.C, g, equivalentClass=[EX.D]),), {})


def intersection_of():
    """Exercises the triples_choices branch and the manchesterSyntax call."""
    g = Graph()
    lst = BNode("list")  # stable id: the fixture is built once per side
    Collection(g, lst, [EX.A, EX.B])
    g.add((EX.C, RDF.type, OWL.Class))
    g.add((EX.C, OWL.intersectionOf, lst))
    return ((StubClass(EX.C, g),), {})


def complement_of():
    g = Graph()
    g.add((EX.C, RDF.type, OWL.Class))
    return ((StubClass(EX.C, g, complementOf=EX.D),), {})


VERDICT = run_pair(__file__, entry="isPrimitive",
                   calls=[plain_named_class, restriction,
                          with_equivalent_class, intersection_of,
                          complement_of])

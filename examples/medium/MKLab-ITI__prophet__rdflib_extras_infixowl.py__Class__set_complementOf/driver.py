"""Validation driver: Class._set_complementOf adds one triple to self.graph.

`self` is a stand-in exposing just what the region reads (`identifier`,
`graph`); it is rebuilt per side by the fixture so the graph stays fresh, and
its `__eq__` compares identifier plus graph isomorphism.
"""
from rdflib import BNode, Graph, URIRef

from infixowl_shim import Class
from rdfeval.harness import graphs_isomorphic, run_pair


class SelfStub:
    """Stand-in for the infixowl Class instance the method is bound to."""

    def __init__(self, identifier):
        self.identifier = identifier
        self.graph = Graph()

    def __eq__(self, other):
        return (isinstance(other, SelfStub)
                and self.identifier == other.identifier
                and graphs_isomorphic(self.graph, other.graph))

    def __repr__(self):
        return f"SelfStub({self.identifier!r}, {len(self.graph)} triples)"


def fixture_uriref_other():
    return ((SelfStub(URIRef("https://example.org/Widget")),
             URIRef("https://example.org/NotAWidget")), {})


# One shared instance: `other` is only read, and the harness compares the
# arguments the two sides received, so it has to be the very same object.
OTHER_CLASS = Class(URIRef("https://example.org/NotAWidget"))


def fixture_class_other():
    """`other` as an infixowl Class: classOrIdentifier unwraps its identifier."""
    return ((SelfStub(URIRef("https://example.org/Widget")), OTHER_CLASS), {})


def fixture_bnode_subject():
    return ((SelfStub(BNode("anon")), URIRef("https://example.org/NotAWidget")), {})


def fixture_falsy_other():
    """`not other` short-circuits: nothing is added."""
    return ((SelfStub(URIRef("https://example.org/Widget")), None), {})


VERDICT = run_pair(__file__, entry="_set_complementOf",
                   calls=[fixture_uriref_other, fixture_class_other,
                          fixture_bnode_subject, fixture_falsy_other])

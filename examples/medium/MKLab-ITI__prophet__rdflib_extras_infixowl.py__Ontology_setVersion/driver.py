"""Validation driver: Ontology.setVersion writes into the instance's graph.

The region is extracted as a free function still taking ``self``, so the
fixtures supply a small stand-in carrying the two attributes it touches
(``identifier`` and ``graph``).  The stand-in compares equal when the
identifiers match and the graphs are isomorphic, so the harness sees the
side effect of the call.
"""
from rdflib import Graph, Literal, Namespace, URIRef

from rdfeval.harness import graphs_isomorphic, run_pair

EX = Namespace("http://example.com/")


class OntologyStub:
    def __init__(self, identifier, graph):
        self.identifier = identifier
        self.graph = graph

    def __eq__(self, other):
        return (isinstance(other, OntologyStub)
                and self.identifier == other.identifier
                and graphs_isomorphic(self.graph, other.graph))

    def __hash__(self):
        return hash(self.identifier)

    def __repr__(self):
        return "OntologyStub(%r, %d triples)" % (self.identifier,
                                                 len(self.graph))


def empty_ontology():
    """setVersion on a graph that carries no versionInfo yet."""
    return ((OntologyStub(EX.myOntology, Graph()), Literal("1.0")), {})


def already_versioned():
    """graph.set() replaces an existing versionInfo rather than adding."""
    g = Graph()
    g.add((EX.myOntology, URIRef("http://www.w3.org/2002/07/owl#versionInfo"),
           Literal("0.9")))
    g.add((EX.myOntology, URIRef("http://example.com/keepMe"), Literal("x")))
    return ((OntologyStub(EX.myOntology, g), Literal("2.0")), {})


VERDICT = run_pair(__file__, entry="setVersion",
                   calls=[empty_ontology, already_versioned])

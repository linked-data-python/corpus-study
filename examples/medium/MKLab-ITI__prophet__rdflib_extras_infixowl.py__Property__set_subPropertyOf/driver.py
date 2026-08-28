"""Validation driver: _set_subPropertyOf writes rdfs:subPropertyOf into self.graph.

The region is an unbound method of infixowl's ``Property``; the fixtures below
supply a stand-in ``self`` (the method only reads ``self.graph`` and
``self.identifier``) whose equality is graph isomorphism, so the harness can
compare the two runs.
"""
from rdflib import BNode, Graph, URIRef

from rdfeval.harness import graphs_isomorphic, run_pair

EX = "http://example.org/"


class Owner:
    def __init__(self, graph, identifier):
        self.graph = graph
        self.identifier = identifier

    def __eq__(self, other):
        return (isinstance(other, Owner)
                and self.identifier == other.identifier
                and graphs_isomorphic(self.graph, other.graph))


def no_parents():
    return ((Owner(Graph(), URIRef(EX + "hasTopping")), []), {})


def uriref_parents():
    return ((Owner(Graph(), URIRef(EX + "hasTopping")),
             [URIRef(EX + "hasIngredient"), URIRef(EX + "hasPart")]), {})


def bnode_parent():
    return ((Owner(Graph(), URIRef(EX + "hasTopping")), [BNode("anon1")]), {})


VERDICT = run_pair(__file__, entry="_set_subPropertyOf",
                   calls=[no_parents, uriref_parents, bnode_parent])

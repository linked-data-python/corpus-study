"""Validation driver for Class._set_disjointWith.

The region is a method lifted out of infixowl's ``Class``; it only reads
``self.identifier`` / ``self.graph``, so the fixtures pass a small holder
whose equality is graph isomorphism.  ``other`` is exercised with plain
IRIs, with infixowl ``Class`` objects (so ``classOrIdentifier`` takes its
other branch), and empty (early return).
"""
from rdflib import BNode, Graph, URIRef

from rdfeval.harness import run_pair, graphs_isomorphic

from infixowl_context import Class

EX = "http://example.org/"


class Holder:
    """Stand-in for the infixowl instance the method is bound to."""

    def __init__(self, identifier, graph):
        self.identifier = identifier
        self.graph = graph

    def __eq__(self, other):
        return (self.identifier == other.identifier
                and graphs_isomorphic(self.graph, other.graph))

    def __repr__(self):
        return f"Holder({self.identifier!r}, {len(self.graph)} triples)"


def case_iris():
    return ((Holder(URIRef(EX + "A"), Graph()),
             [URIRef(EX + "B"), URIRef(EX + "C")]), {})


def case_class_objects():
    g = Graph()
    return ((Holder(URIRef(EX + "A"), g),
             [Class(URIRef(EX + "D"), graph=g), BNode("anon")]), {})


def case_empty():
    return ((Holder(URIRef(EX + "A"), Graph()), []), {})


VERDICT = run_pair(__file__, entry="_set_disjointWith",
                   calls=[case_iris, case_class_objects, case_empty])

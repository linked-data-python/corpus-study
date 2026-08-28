"""Validation driver for Individual._set_type.

The region is a method lifted out of infixowl's ``Individual``; it only
reads ``self.identifier`` / ``self.graph``, so the fixtures pass a small
holder whose equality is graph isomorphism.  ``kind`` is exercised on all
four paths: a bare identifier, an ``Individual`` subclass instance, an
iterable of identifiers, and the falsy early return.
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


def case_identifier():
    return ((Holder(URIRef(EX + "i"), Graph()), URIRef(EX + "C")), {})


def case_individual():
    g = Graph()
    return ((Holder(URIRef(EX + "i"), g), Class(URIRef(EX + "C"), graph=g)), {})


def case_iterable():
    return ((Holder(URIRef(EX + "i"), Graph()),
             [URIRef(EX + "C"), URIRef(EX + "D"), BNode("anon")]), {})


def case_empty():
    return ((Holder(URIRef(EX + "i"), Graph()), None), {})


VERDICT = run_pair(__file__, entry="_set_type",
                   calls=[case_identifier, case_individual, case_iterable,
                          case_empty])

"""Validation driver for Class._get_extentQuery.

The region is a one-line property getter: it returns the triple pattern
``(?CLASS, rdf:type, <this class>)`` that infixowl later hands to
``graph.triples()``.  The driver supplies a stand-in ``self`` carrying the
only attribute the region reads, and the harness compares the returned
tuple term by term.
"""
from rdflib import BNode, URIRef

from rdfeval.harness import run_pair


class Owner:
    """Stands in for the infixowl Class whose extent query is asked for."""

    def __init__(self, identifier):
        self.identifier = identifier

    def __eq__(self, other):
        return isinstance(other, Owner) and self.identifier == other.identifier

    def __repr__(self):
        return "Owner(%r)" % (self.identifier,)


def named_class():
    return ((Owner(URIRef("http://example.org/ns#Pizza")),), {})


def anonymous_class():
    return ((Owner(BNode("anonymous_class")),), {})


VERDICT = run_pair(__file__, entry="_get_extentQuery",
                   calls=[named_class, anonymous_class])

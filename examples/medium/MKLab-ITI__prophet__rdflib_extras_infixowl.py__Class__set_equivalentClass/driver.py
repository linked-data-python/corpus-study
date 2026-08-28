"""Validation driver: Class._set_equivalentClass writes owl:equivalentClass.

The region is a method body, so the driver supplies a stand-in ``self``
carrying the two attributes it touches (``graph`` and ``identifier``).
Fixtures cover both arms of ``classOrIdentifier``: bare identifiers and
wrapped infixowl class objects, plus the falsy early return.
"""
from rdflib import BNode, Graph, URIRef

from infixowl_context import Class
from rdfeval.harness import graphs_isomorphic, run_pair


class _Term:
    """Stand-in for the infixowl Class instance being mutated."""

    def __init__(self):
        self.graph = Graph()
        self.identifier = URIRef("http://example.org/Pizza")

    def __eq__(self, other):
        if not isinstance(other, _Term):
            return NotImplemented
        return (self.identifier == other.identifier
                and graphs_isomorphic(self.graph, other.graph))


def identifiers():
    return ((_Term(), [URIRef("http://example.org/Pie"), BNode("b1")]), {})


def class_objects():
    return ((_Term(), [Class(URIRef("http://example.org/Pie"))]), {})


def empty():
    return ((_Term(), []), {})


VERDICT = run_pair(__file__, entry="_set_equivalentClass",
                   calls=[identifiers, class_objects, empty])

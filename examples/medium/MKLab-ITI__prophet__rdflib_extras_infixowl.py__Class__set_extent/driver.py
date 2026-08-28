"""Validation driver for MKLab-ITI__prophet__rdflib_extras_infixowl.py__Class__set_extent.

`_set_extent` is the setter behind infixowl's ``Class.extent`` property: it
asserts ``rdf:type`` for every member of ``other`` in ``self.graph``.  The
region was extracted as a module-level function, so it is called directly
with a stand-in owner object carrying the two attributes it reads
(``graph``, ``identifier``).  The owner compares by graph isomorphism, so
the harness sees the RDF effect of the call.
"""
import sys

sys.dont_write_bytecode = True  # the shim next to this driver is imported

from rdflib import BNode, Graph, URIRef

from rdfeval.harness import graphs_isomorphic, run_pair

from infixowl_shim import Class

EX = "http://example.org/pizza#"


class Owner:
    """Stands in for the infixowl Class instance that owns the setter."""

    def __init__(self, identifier):
        self.graph = Graph()
        self.identifier = identifier

    def __eq__(self, other):
        return (isinstance(other, Owner)
                and self.identifier == other.identifier
                and graphs_isomorphic(self.graph, other.graph))

    def __repr__(self):
        return "Owner(%s, %d triples)" % (self.identifier, len(self.graph))


# shared instances so that the two fixture invocations yield equal arguments
MEMBERS = [URIRef(EX + "margherita"), BNode("m2"), Class(URIRef(EX + "napoli"))]


def with_members():
    return ((Owner(URIRef(EX + "Pizza")), list(MEMBERS)), {})


def empty_extent():
    return ((Owner(URIRef(EX + "Pizza")), []), {})


VERDICT = run_pair(__file__, entry="_set_extent",
                   calls=[with_members, empty_extent])

"""Validation driver for MKLab-ITI__prophet__rdflib_extras_infixowl.py__Individual__set_identifier.

`_set_identifier` renames an infixowl Individual: it moves every incoming and
outgoing statement of the old identifier onto the new one, then recomputes the
qname.  The region was extracted as a module-level function, so ``self.__identifier``
is NOT name-mangled here and the attribute is set with ``setattr``.  The owner
compares by graph isomorphism plus the two scalar attributes the region writes.
"""
from rdflib import BNode, Graph, Literal, URIRef

from rdfeval.harness import graphs_isomorphic, run_pair

EX = URIRef("http://example.org/ns#")


class Owner:
    """Stands in for the infixowl Individual whose identifier is being set."""

    def __init__(self, identifier, graph):
        self.graph = graph
        # module-level extraction: the region reads a plain "__identifier"
        setattr(self, "__identifier", identifier)
        self.qname = None

    def __eq__(self, other):
        return (isinstance(other, Owner)
                and getattr(self, "__identifier") == getattr(other, "__identifier")
                and self.qname == other.qname
                and graphs_isomorphic(self.graph, other.graph))

    def __repr__(self):
        return "Owner(%s, qname=%r, %d triples)" % (
            getattr(self, "__identifier"), self.qname, len(self.graph))


OLD = URIRef("http://example.org/ns#old")
NEW = URIRef("http://example.org/ns#new")
OTHER = URIRef("http://example.org/ns#other")


def _populated():
    g = Graph()
    g.bind("ex", "http://example.org/ns#")
    g.add((OLD, URIRef("http://example.org/ns#label"), Literal("an individual")))
    g.add((OTHER, URIRef("http://example.org/ns#knows"), OLD))
    return g


def rename_to_uriref():
    return ((Owner(OLD, _populated()), NEW), {})


def rename_to_bnode():
    return ((Owner(OLD, _populated()), BNode("target")), {})


def rename_to_same():
    return ((Owner(OLD, _populated()), OLD), {})


VERDICT = run_pair(__file__, entry="_set_identifier",
                   calls=[rename_to_uriref, rename_to_bnode, rename_to_same])

"""Validation driver for MKLab-ITI__prophet__rdflib_extras_infixowl.py__Property__set_inverseOf.

`_set_inverseOf` is the setter behind infixowl's ``Property.inverseOf``: it
asserts one ``owl:inverseOf`` triple in ``self.graph``.  The region was
extracted as a module-level function, so it is called directly with a
stand-in owner carrying the two attributes it reads (``graph``,
``identifier``); the owner compares by graph isomorphism so the harness sees
the RDF effect.  The second fixture exercises the early ``return``.
"""
import sys

sys.dont_write_bytecode = True  # the shim next to this driver is imported

from rdflib import Graph, URIRef

from rdfeval.harness import graphs_isomorphic, run_pair

from infixowl_shim import Property

EX = "http://example.org/ns#"


class Owner:
    """Stands in for the infixowl Property instance that owns the setter."""

    def __init__(self, identifier):
        self.graph = Graph()
        self.identifier = identifier

    def __eq__(self, other):
        return (isinstance(other, Owner)
                and self.identifier == other.identifier
                and graphs_isomorphic(self.graph, other.graph))

    def __repr__(self):
        return "Owner(%s, %d triples)" % (self.identifier, len(self.graph))


# shared instance so that the two fixture invocations yield equal arguments
OTHER = Property(URIRef(EX + "isPartOf"))


def with_property():
    return ((Owner(URIRef(EX + "hasPart")), OTHER), {})


def with_uriref():
    return ((Owner(URIRef(EX + "hasPart")), URIRef(EX + "isPartOf")), {})


def with_none():
    return ((Owner(URIRef(EX + "hasPart")), None), {})


VERDICT = run_pair(__file__, entry="_set_inverseOf",
                   calls=[with_property, with_uriref, with_none])

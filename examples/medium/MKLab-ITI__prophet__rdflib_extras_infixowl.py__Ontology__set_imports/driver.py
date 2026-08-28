"""Validation driver for MKLab-ITI__prophet__rdflib_extras_infixowl.py__Ontology__set_imports.

`_set_imports` is the setter behind infixowl's ``Ontology.imports``: it
asserts one ``owl:imports`` triple per element of ``other``.  The region was
extracted as a module-level function, so it is called directly with a
stand-in owner carrying the two attributes it reads (``graph``,
``identifier``); the owner compares by graph isomorphism so the harness sees
the RDF effect.  The second fixture exercises the early ``return``.
"""
from rdflib import Graph, URIRef

from rdfeval.harness import graphs_isomorphic, run_pair


class Owner:
    """Stands in for the infixowl Ontology instance that owns the setter."""

    def __init__(self, identifier):
        self.graph = Graph()
        self.identifier = identifier

    def __eq__(self, other):
        return (isinstance(other, Owner)
                and self.identifier == other.identifier
                and graphs_isomorphic(self.graph, other.graph))

    def __repr__(self):
        return "Owner(%s, %d triples)" % (self.identifier, len(self.graph))


ONT = URIRef("http://example.org/my-ontology")
IMPORTS = [URIRef("http://www.w3.org/2004/02/skos/core"),
           URIRef("http://xmlns.com/foaf/0.1/")]


def with_imports():
    return ((Owner(ONT), list(IMPORTS)), {})


def with_none():
    return ((Owner(ONT), None), {})


VERDICT = run_pair(__file__, entry="_set_imports",
                   calls=[with_imports, with_none])

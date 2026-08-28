"""Validation driver for AnnotatableTerms._set_seeAlso.

The region is a property setter body: it asserts one rdfs:seeAlso statement
per element of the argument.  The driver supplies a stand-in ``self`` with the
two attributes the region reads (``graph``, ``identifier``) and compares it
after each call — by graph isomorphism, so both representations must have
built the same statements.
"""
from rdflib import BNode, Graph, Literal, URIRef

from rdfeval.harness import graphs_isomorphic, run_pair

EX = "http://example.org/ns#"
SUBJECT = URIRef(EX + "Pizza")


class Owner:
    """Stands in for the infixowl AnnotatableTerms whose seeAlso is being set."""

    def __init__(self, identifier=SUBJECT):
        self.identifier = identifier
        self.graph = Graph()
        # a pre-existing statement, so an empty argument is visibly a no-op
        self.graph.add((identifier, URIRef(EX + "label"), Literal("Pizza")))

    def __eq__(self, other):
        return (isinstance(other, Owner)
                and self.identifier == other.identifier
                and graphs_isomorphic(self.graph, other.graph))

    def __repr__(self):
        return "Owner(%s, %d triples)" % (self.identifier, len(self.graph))


def two_uris():
    return ((Owner(), [URIRef("http://dbpedia.org/resource/Pizza"),
                       URIRef("http://www.wikidata.org/entity/Q177")]), {})


def mixed_terms():
    # rdfs:seeAlso is unconstrained in RDF; infixowl asserts whatever it is given
    return ((Owner(), [URIRef(EX + "Calzone"),
                       Literal("see the cookbook"),
                       BNode("anonymous_reference")]), {})


def bnode_subject():
    return ((Owner(BNode("anonymous_class")), [URIRef(EX + "Calzone")]), {})


def empty():
    return ((Owner(), []), {})


def none():
    return ((Owner(), None), {})


VERDICT = run_pair(__file__, entry="_set_seeAlso",
                   calls=[two_uris, mixed_terms, bnode_subject, empty, none])

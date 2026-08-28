"""Validation driver: Query.get_schema_org_metadata_graph projects an
ontology's DCTERMS metadata onto schema.org terms and returns a fresh Graph.

The region is extracted as a free function still taking ``self``, so the
fixtures supply a stand-in carrying the single attribute it touches
(``graph``).  The returned Graph is compared by isomorphism.  The fixtures
between them cover all three entry types (owl:Ontology, skos:ConceptScheme,
prof:Profile), every DCTERMS branch of the elif chain, and both shapes of a
publisher/creator/contributor value: a plain Literal and a node whose
AGENT_PROPS are copied across (including a blank node, which exercises the
isomorphism comparison rather than plain equality).
"""
from rdflib import Graph

from rdfeval.harness import graphs_isomorphic, run_pair

FULL_METADATA = """
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix owl:     <http://www.w3.org/2002/07/owl#> .
@prefix sdo:     <https://schema.org/> .
@prefix xsd:     <http://www.w3.org/2001/XMLSchema#> .

<http://example.com/onto> a owl:Ontology ;
    dcterms:title "An ontology"@en ;
    dcterms:description "It describes things." ;
    dcterms:publisher <http://example.com/org> ;
    dcterms:creator [ sdo:name "Ada" ; sdo:email "ada@example.com" ;
                      sdo:unknownProp "dropped" ] ;
    dcterms:contributor "Just a name" ;
    dcterms:created "2020-01-01"^^xsd:date ;
    dcterms:modified "2021-02-03"^^xsd:date ;
    dcterms:issued "2020-06-01"^^xsd:date ;
    dcterms:license <http://example.com/licence> ;
    dcterms:rights "(c) Example" ;
    dcterms:source <http://example.com/ignored> .

<http://example.com/org>
    sdo:name "Example Org" ;
    sdo:url <http://example.com/> ;
    sdo:notAnAgentProp "dropped" .
"""

SCHEME_AND_PROFILE = """
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix prof:    <http://www.w3.org/ns/dx/prof/> .
@prefix skos:    <http://www.w3.org/2004/02/skos/core#> .

<http://example.com/scheme> a skos:ConceptScheme ;
    dcterms:title "A scheme" .

<http://example.com/profile> a prof:Profile ;
    dcterms:description "A profile" .
"""

NOTHING_MATCHING = """
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
<http://example.com/thing> rdfs:label "not an ontology" .
"""


class QueryStub:
    def __init__(self, turtle):
        self.graph = Graph()
        self.graph.parse(data=turtle, format="turtle")

    def __eq__(self, other):
        return (isinstance(other, QueryStub)
                and graphs_isomorphic(self.graph, other.graph))

    def __hash__(self):
        return 0

    def __repr__(self):
        return "QueryStub(%d triples)" % len(self.graph)


def full_metadata():
    return ((QueryStub(FULL_METADATA),), {})


def scheme_and_profile():
    return ((QueryStub(SCHEME_AND_PROFILE),), {})


def nothing_matching():
    return ((QueryStub(NOTHING_MATCHING),), {})


VERDICT = run_pair(__file__, entry="get_schema_org_metadata_graph",
                   calls=[full_metadata, scheme_and_profile, nothing_matching])

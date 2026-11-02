"""Driver for VocPub._extract_concept_scheme.

`self` is a stand-in for the pyLODE VocPub profile: only the attributes the
region touches (G, METADATA, COLLECTIONS, CONCEPTS, outputformat) and the two
helper methods it calls.  The graph G is the fixture (or an inline variant).
"""
from pathlib import Path

from rdflib import BNode, Graph, URIRef
from rdflib.namespace import SDO

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
PREFIXES = """
@prefix ex: <http://example.org/> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix doap: <http://usefulinc.com/ns/doap#> .
@prefix sdo: <https://schema.org/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
"""


class FakeVocPub:
    """The few members of pylode's VocPub that _extract_concept_scheme uses."""

    def __init__(self, G, outputformat="html", metadata=None,
                 collections=None, concepts=None):
        self.G = G
        self.outputformat = outputformat
        self.METADATA = {} if metadata is None else metadata
        self.COLLECTIONS = {} if collections is None else collections
        self.CONCEPTS = {} if concepts is None else concepts

    def _make_formatted_uri(self, uri):
        return '<a href="{0}">{0}</a>'.format(str(uri))

    def _make_agent(self, agent):
        if isinstance(agent, BNode):          # a blank node is named, never printed
            return "agent:" + str(self.G.value(agent, SDO.name))
        return self._make_formatted_uri(agent)


def _inline(turtle, **kw):
    return lambda: ((FakeVocPub(Graph().parse(data=PREFIXES + turtle, format="turtle"), **kw),), {})


def _fixture(**kw):
    return lambda: ((FakeVocPub(fixture_graph(FIXTURE), **kw),), {})


CALLS = [
    # every branch, html output (description and historyNote go through markdown)
    _fixture(),
    # md output keeps the raw text; collections and concepts flagged
    _fixture(outputformat="md", collections={"c": 1}, concepts={"k": 2}),
    # two schemes: the loop runs once per scheme (the last one wins, in both)
    _inline("""
        ex:s1 a skos:ConceptScheme ; skos:prefLabel "First" ; dcterms:creator "A" .
        ex:s2 a skos:ConceptScheme ; skos:prefLabel "Second" ; dcterms:creator "B" ;
              dcterms:contributor ex:c1 .
        """),
    # non-http source / licence, a wasGeneratedBy without doap:repository, a
    # literal wasGeneratedBy (nothing to look up), two repositories on one object
    _inline("""
        ex:s a skos:ConceptScheme ; skos:prefLabel "T" ;
           dcterms:source "a printed book" ;
           dcterms:license "CC BY 4.0" ;
           dcterms:rights "(c) someone" ;
           prov:wasGeneratedBy ex:nogen , "a literal activity" , [ doap:repository ex:r1 , ex:r2 ] .
        ex:nogen sdo:name "no repository here" .
        """),
    # no title on the scheme: the region raises
    _inline("""
        ex:s a skos:ConceptScheme ; dcterms:creator "Nobody" ;
             dcterms:description "no prefLabel" .
        ex:t a skos:Concept ; skos:prefLabel "belongs to a concept" .
        """),
    # no scheme at all (an owl:Ontology is NOT a scheme here): zero solutions;
    # the title was preset, so the region goes on to the collections checks
    _inline("""
        ex:o a owl:Ontology ; skos:prefLabel "ontology" ; dcterms:creator "Z" .
        """, metadata={"title": "preset"}, collections={"c": 1}),
]

VERDICT = run_pair(__file__, entry="_extract_concept_scheme", fixture="fixture.ttl", calls=CALLS)

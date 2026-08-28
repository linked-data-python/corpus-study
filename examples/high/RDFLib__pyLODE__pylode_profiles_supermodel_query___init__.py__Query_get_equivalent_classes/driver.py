"""Validation driver: Query.get_equivalent_classes reads owl:equivalentClass.

`self` is only used for `self.db` (the union dataset get_name falls back to),
so the fixture passes one shared stand-in object holding a small Dataset: the
same object goes to both sides, which keeps the harness's argument comparison
meaningful (the fresh profile Graph is still compared by isomorphism).
"""
from rdflib import Dataset, Graph, URIRef

from rdfeval.harness import run_pair

PROFILE = """
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix ex:   <https://example.org/> .

ex:Widget owl:equivalentClass ex:Gadget, ex:Doohickey, ex:Ignored,
                              [ a owl:Class ] .
ex:Gadget    rdfs:label "Zeta gadget" .
ex:Doohickey skos:prefLabel "Alpha doohickey" .
ex:Ignored   rdfs:label "Ignored class" .
"""

# The union dataset get_name falls back to when the profile graph has no name.
DB = Dataset()
DB.parse(data="""
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ex:   <https://example.org/> .
ex:Doohickey rdfs:label "label only in the db" .
""", format="turtle")


class QueryStub:
    """Stand-in for the Query instance: the region only reads self.db."""

    db = DB


SELF = QueryStub()


def _profile_graph():
    g = Graph()
    g.parse(data=PROFILE, format="turtle")
    return g


def fixture_with_equivalents():
    return ((SELF, URIRef("https://example.org/Widget"), _profile_graph(),
             [URIRef("https://example.org/Ignored")]), {})


def fixture_none():
    return ((SELF, URIRef("https://example.org/Gadget"), _profile_graph(), []), {})


VERDICT = run_pair(__file__, entry="get_equivalent_classes",
                   calls=[fixture_with_equivalents, fixture_none])

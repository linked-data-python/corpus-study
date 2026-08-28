"""Validation driver: CastClass inspects a graph and picks which infixowl
wrapper to build.  The four fixtures below cover its four exits (Restriction,
EnumeratedClass, BooleanClass, plain Class); the returned stand-ins compare
equal iff both sides constructed them from the same arguments, with the graph
argument compared by isomorphism.
"""
from rdflib import Graph, URIRef

from rdfeval.harness import run_pair

ONTOLOGY = """
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ex:   <https://example.org/> .

ex:HasPartSomeThing a owl:Restriction ;
    owl:onProperty ex:hasPart ;
    owl:someValuesFrom ex:Thing ;
    owl:maxCardinality 3 ;
    rdfs:comment "a predicate that is not a restriction kind, hence skipped" .

ex:UnionClass a owl:Class ;
    owl:unionOf ( ex:Alpha ex:Beta ) .

ex:EnumClass a owl:Class ;
    owl:oneOf ( ex:one ex:two ) .

ex:PlainClass a owl:Class ;
    rdfs:label "no boolean construct at all" .
"""


def _graph():
    g = Graph()
    g.parse(data=ONTOLOGY, format="turtle")
    return g


def _fixture(local):
    return lambda: ((URIRef("https://example.org/" + local), _graph()), {})


VERDICT = run_pair(__file__, entry="CastClass",
                   calls=[_fixture("HasPartSomeThing"),   # -> Restriction
                          _fixture("UnionClass"),         # -> BooleanClass
                          _fixture("EnumClass"),          # -> EnumeratedClass
                          _fixture("PlainClass")])        # -> Class

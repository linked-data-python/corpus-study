"""Validation driver for RDFLib__pyLODE__…__Query_get_onts_props.

``get_onts_props`` is a method that only reads ``self.graph``; the fixtures
stand in for the Query object with a SimpleNamespace holding a freshly parsed
graph (fixed identifier, so the harness can also compare the arguments).
"""
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))  # rdf_elements shim

from rdflib import Graph, URIRef

from rdfeval.harness import run_pair

TTL = """
@prefix prof:    <http://www.w3.org/ns/dx/prof/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix owl:     <http://www.w3.org/2002/07/owl#> .
@prefix sdo:     <https://schema.org/> .
@prefix ex:      <http://example.com/> .

ex:profile a prof:Profile ;
    dcterms:title "A profile"@en ;
    dcterms:created "2024-01-01" ;
    dcterms:description "…" ;
    owl:versionIRI ex:profile-1.0 ;
    sdo:codeRepository <https://example.com/repo> ;
    ex:notAnOntologyProp "ignored" .

ex:other a prof:Profile ;
    dcterms:title "Another profile"@en .

ex:notAProfile a owl:Ontology ;
    dcterms:title "Not collected" .
"""


def query_object():
    g = Graph(identifier=URIRef("http://example.com/g"))
    g.parse(data=TTL, format="turtle")
    return ((SimpleNamespace(graph=g),), {})


def empty_query_object():
    g = Graph(identifier=URIRef("http://example.com/g"))
    return ((SimpleNamespace(graph=g),), {})


VERDICT = run_pair(__file__, entry="get_onts_props",
                   calls=[query_object, empty_query_object])

"""Validation driver for RDFLib__pyLODE__…__Query_get_title.

``get_title`` only reads ``self.graph``; the fixtures stand in for the Query
object with a SimpleNamespace holding a freshly parsed graph (fixed
identifier, so the harness can also compare the arguments).
"""
from types import SimpleNamespace

from rdflib import Graph, URIRef

from rdfeval.harness import run_pair

TTL = """
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix dc:      <http://purl.org/dc/elements/1.1/> .
@prefix ex:      <http://example.com/> .

ex:onto  dcterms:title "A vocabulary"@en .
ex:other dc:title "Dublin Core 1.1 title, not dcterms" .
"""


def _query():
    g = Graph(identifier=URIRef("http://example.com/g"))
    g.parse(data=TTL, format="turtle")
    return SimpleNamespace(graph=g)


def titled():
    return ((_query(), URIRef("http://example.com/onto")), {})


def untitled():
    return ((_query(), URIRef("http://example.com/other")), {})


def unknown():
    return ((_query(), URIRef("http://example.com/nope")), {})


VERDICT = run_pair(__file__, entry="get_title",
                   calls=[titled, untitled, unknown])

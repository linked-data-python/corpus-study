"""Validation driver: Query.get_ns returns (prefix, namespace) for an ontology
graph, and -- in the owl:Ontology branch -- also writes a prof:Profile type
back into that graph.

The region is extracted as a free function still taking ``self``, so the
fixtures supply a stand-in carrying the single attribute it touches
(``graph``); the stand-in compares equal when the graphs are isomorphic, so
the harness sees the write as well as the returned tuple.  Fixtures cover the
three paths that return: the declared VANN namespace, an existing
prof:Profile, and the owl:Ontology fallback that adds the triple.  The fourth
path raises and is not exercised (an exception aborts the whole comparison).
"""
from rdflib import Graph

from rdfeval.harness import graphs_isomorphic, run_pair

VANN_DECLARED = """
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix vann: <http://purl.org/vocab/vann/> .
<http://example.com/onto> a owl:Ontology ;
    vann:preferredNamespaceUri "http://example.com/onto#" ;
    vann:preferredNamespacePrefix "ex" .
"""

PROFILE_DECLARED = """
@prefix prof: <http://www.w3.org/ns/dx/prof/> .
<http://example.com/profiles/myProfile> a prof:Profile .
"""

ONTOLOGY_ONLY = """
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
<http://example.com/onto2> a owl:Ontology ;
    rdfs:label "Second ontology" .
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


def vann_declared():
    return ((QueryStub(VANN_DECLARED),), {})


def profile_declared():
    return ((QueryStub(PROFILE_DECLARED),), {})


def ontology_only():
    """Falls through to the owl:Ontology branch, which adds prof:Profile."""
    return ((QueryStub(ONTOLOGY_ONLY),), {})


VERDICT = run_pair(__file__, entry="get_ns",
                   calls=[vann_declared, profile_declared, ontology_only])

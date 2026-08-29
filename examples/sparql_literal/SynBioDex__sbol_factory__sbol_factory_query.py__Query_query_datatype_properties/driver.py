"""Validation driver for SynBioDex__sbol_factory__sbol_factory_query.py__Query_query_datatype_properties.

The region is a method: it reads only `self.graph`, so each fixture passes a
stand-in `Self` holding a fresh graph (built inline, no fixture.ttl -- the
region's oracle is "isomorphism" in meta.json, not "values").

The fixture graph exercises both SELECT queries the region runs:

  * ex:directProp    -- rdfs:domain ex:A directly (the property path's zero
                         application)
  * ex:unionProp     -- domain is an owl:unionOf list that CONTAINS ex:A
                         (the property path's recursive branch)
  * ex:restrictedProp -- reached only through the second query, via
                         ex:A rdfs:subClassOf [ owl:onProperty ex:restrictedProp ]

and the neighbourhood that must NOT show up for ex:A:

  * ex:objProp              -- domain ex:A, but owl:ObjectProperty (wrong type)
  * ex:otherDirectProp      -- owl:DatatypeProperty, but domain ex:B
  * ex:objRestrictedProp    -- reached from ex:B's restriction, wrong type
  * ex:unrelatedUnionProp   -- a unionOf list that does NOT contain ex:A

Three calls: ex:A (several solutions from both queries), ex:B (the
neighbourhood's own positive case, to make sure it is not a red herring),
and ex:Empty (zero solutions from either query).
"""
from rdflib import Graph

from rdfeval.harness import graphs_isomorphic, run_pair

GRAPH_TTL = """
@prefix ex:   <http://example.org/> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:directProp a owl:DatatypeProperty ; rdfs:domain ex:A .
ex:unionProp a owl:DatatypeProperty ;
    rdfs:domain [ owl:unionOf ( ex:OtherClass ex:A ) ] .
ex:restrictedProp a owl:DatatypeProperty .
ex:A rdfs:subClassOf [ a owl:Restriction ; owl:onProperty ex:restrictedProp ] .

ex:objProp a owl:ObjectProperty ; rdfs:domain ex:A .
ex:otherDirectProp a owl:DatatypeProperty ; rdfs:domain ex:B .
ex:objRestrictedProp a owl:ObjectProperty .
ex:B rdfs:subClassOf [ a owl:Restriction ; owl:onProperty ex:objRestrictedProp ] .
ex:unrelatedUnionProp a owl:DatatypeProperty ;
    rdfs:domain [ owl:unionOf ( ex:OtherClass ex:YetAnother ) ] .
"""


class Self:
    """Stand-in for the enclosing sbol_factory.query.Query: the region reads
    only self.graph."""

    def __init__(self, graph):
        self.graph = graph

    def __eq__(self, other):
        return isinstance(other, Self) and graphs_isomorphic(self.graph, other.graph)

    def __hash__(self):
        return 0


def _graph():
    return Graph().parse(data=GRAPH_TTL, format="turtle")


def call(class_uri):
    return lambda: ((Self(_graph()), class_uri), {})


VERDICT = run_pair(
    __file__,
    entry="query_datatype_properties",
    calls=[
        call("http://example.org/A"),
        call("http://example.org/B"),
        call("http://example.org/Empty"),
    ],
    ordered=False,  # the region's own result goes through list(set(...))
)

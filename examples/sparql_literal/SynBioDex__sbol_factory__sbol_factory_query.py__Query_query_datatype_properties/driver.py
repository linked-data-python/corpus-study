"""Validation driver for SynBioDex__sbol_factory__sbol_factory_query.py__Query_query_datatype_properties.

The region is a method: it reads only `self.graph`, so each fixture passes a
stand-in `Self` holding a fresh graph (built inline, no fixture.ttl -- the
region's oracle is "isomorphism" in meta.json, not "values").

The fixture graph exercises both SELECT queries the region runs:

  * ex:directProp    -- rdfs:domain ex:A directly (the property path's zero
                         application)
  * ex:unionProp     -- domain is an owl:unionOf list that CONTAINS ex:A
                         (the property path's recursive branch), at index 1
  * ex:headUnionProp -- ex:A at index 0 of the list: zero rdf:rest
                         (kills rdf:rest* -> rdf:rest+)
  * ex:thirdUnionProp -- ex:A at index 2 of the list: two rdf:rest
                         (kills rdf:rest* -> rdf:rest and -> rdf:rest?)
  * ex:nestedUnionProp -- ex:A inside a union nested in a union: two
                         applications of the outer (owl:unionOf/...)*
                         (kills the outer * -> ?)
  * ex:restrictedProp -- reached only through the second query, via
                         ex:A rdfs:subClassOf [ owl:onProperty ex:restrictedProp ]

and the neighbourhood that must NOT show up for ex:A:

  * ex:objProp              -- domain ex:A, but owl:ObjectProperty (wrong type)
  * ex:otherDirectProp      -- owl:DatatypeProperty, but domain ex:B
  * ex:objRestrictedProp    -- reached from ex:B's restriction, wrong type
  * ex:unrelatedUnionProp   -- a unionOf list that does NOT contain ex:A
  * ex:rangeProp            -- owl:DatatypeProperty, ex:A as rdfs:range, not
                               domain (same subject and object, other predicate)
  * ex:intersectionProp     -- ex:A in an owl:intersectionOf list, not unionOf
  * ex:seeAlsoProp          -- domain ex:A, linked to owl:DatatypeProperty by
                               rdfs:seeAlso instead of rdf:type (kills the
                               type predicate widened to a variable)
  * ex:eqProp               -- on a restriction reached from ex:A by
                               owl:equivalentClass, not rdfs:subClassOf
                               (kills rdfs:subClassOf widened to a variable)
  * ex:someValuesProp       -- on ex:A's subClassOf restriction through
                               owl:someValuesFrom, not owl:onProperty
                               (kills owl:onProperty widened to a variable)

Each negative neighbour keeps two of the three terms of the pattern it must
not match, so a mutant that widens the third one changes the result for ex:A.
The region never registers rdflib's CUSTOM_EVALS (custom_eval.py does so only
under __main__ in the repository), so both sides use the default evaluator.
class_uri is a str, as at every real call site (sbol_factory.py:133,238,
uml_factory.py:185,273,347 pass CLASS_URI strings).

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

ex:headUnionProp a owl:DatatypeProperty ;
    rdfs:domain [ owl:unionOf ( ex:A ex:OtherClass ) ] .
ex:thirdUnionProp a owl:DatatypeProperty ;
    rdfs:domain [ owl:unionOf ( ex:OtherClass ex:YetAnother ex:A ) ] .
ex:nestedUnionProp a owl:DatatypeProperty ;
    rdfs:domain [ owl:unionOf ( [ owl:unionOf ( ex:YetAnother ex:A ) ] ex:OtherClass ) ] .

ex:rangeProp a owl:DatatypeProperty ; rdfs:range ex:A .
ex:intersectionProp a owl:DatatypeProperty ;
    rdfs:domain [ owl:intersectionOf ( ex:A ex:OtherClass ) ] .
ex:seeAlsoProp rdfs:seeAlso owl:DatatypeProperty ; rdfs:domain ex:A .
ex:eqProp a owl:DatatypeProperty .
ex:A owl:equivalentClass [ a owl:Restriction ; owl:onProperty ex:eqProp ] .
ex:someValuesProp a owl:DatatypeProperty .
ex:A rdfs:subClassOf [ a owl:Restriction ; owl:someValuesFrom ex:someValuesProp ] .
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

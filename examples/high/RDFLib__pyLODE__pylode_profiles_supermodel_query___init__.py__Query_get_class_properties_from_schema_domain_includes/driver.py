"""Validation driver for Query.get_class_properties_from_schema_domain_includes.

The region is a method that walks every named graph of `self.db` (an rdflib
Dataset) looking for sdo:domainIncludes, so the fixture builds a two-profile
Dataset by hand and passes a duck-typed `self`.  The returned dict of
Property dataclasses is compared field by field (the dataclasses come from
context.py, so both sides use the very same classes).
"""
from collections import defaultdict

from rdflib import Dataset, Graph, URIRef
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID

from rdfeval.harness import run_pair

EX = "https://example.org/"

PROFILE_A = """
@prefix sdo:  <https://schema.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix ex:   <https://example.org/> .

ex:profileA rdfs:label "Profile A" .

ex:name a sdo:Property ;
    rdfs:label "name" ;
    skos:definition "The name of the thing." ;
    sdo:domainIncludes ex:Person ;
    sdo:rangeIncludes ex:Text .

ex:knows sdo:domainIncludes ex:Person ;
    sdo:rangeIncludes ex:Person, ex:Agent .

ex:Employee rdfs:subClassOf ex:Person ; rdfs:label "Employee" .
ex:Person rdfs:label "Person" .
ex:Text rdfs:label "Text" .
ex:Agent rdfs:label "Agent" .

ex:unrelated sdo:domainIncludes ex:Country .
"""

PROFILE_B = """
@prefix sdo:  <https://schema.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ex:   <https://example.org/> .

ex:age sdo:domainIncludes ex:Person ;
    sdo:rangeIncludes ex:Number .
"""


class _Query:
    """Stand-in for pyLODE's Query, as far as the region needs it."""

    def __init__(self):
        self.db = Dataset()
        # materialise the default graph up front: Dataset.contexts() creates it
        # lazily while iterating, which would make the region's
        # `for _graph in self.db.graphs(): self.db.get_graph(...)` blow up with
        # "Set changed size during iteration" (an rdflib quirk, both sides).
        self.db.graph(DATASET_DEFAULT_GRAPH_ID)
        for name, ttl in (("profileA", PROFILE_A), ("profileB", PROFILE_B)):
            g = self.db.graph(URIRef(EX + name))
            g.parse(data=ttl, format="turtle")

    def __eq__(self, other):  # the harness compares arguments after the call
        from rdfeval.harness import normalise
        if not isinstance(other, _Query):
            return False
        mine = {str(g.identifier): normalise(g) for g in self.db.graphs()}
        theirs = {str(g.identifier): normalise(g) for g in other.db.graphs()}
        return mine == theirs


def _call(target, ignored=()):
    def fixture():
        return ((_Query(), URIRef(target), defaultdict(list), list(ignored)), {})
    return fixture


VERDICT = run_pair(
    __file__,
    entry="get_class_properties_from_schema_domain_includes",
    calls=[
        _call(EX + "Person"),                        # two graphs, three matches
        _call(EX + "Person", [URIRef(EX + "Employee")]),  # ignored subclass
        _call(EX + "Nothing"),                       # no match at all
    ],
)

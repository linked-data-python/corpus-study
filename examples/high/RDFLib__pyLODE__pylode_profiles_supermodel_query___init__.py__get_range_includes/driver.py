"""Validation driver: get_range_includes collects the sdo:rangeIncludes
objects of a property and wraps each in a supermodel Class.

The function is pure, so the fixtures pass the two graphs directly.
They cover a property with two range classes (one of which has subclasses, so
get_class recurses), a property whose range class is only named in the union
graph, and a property with no sdo:rangeIncludes at all (empty result).

``db`` is the "union of all graphs" argument, which the region only forwards
to get_class -> get_name, where it is used through .objects(); a plain Graph
is passed rather than a Dataset because the harness compares every Graph-typed
argument by isomorphism and rdflib's isomorphism helper cannot consume the
quads a Dataset yields.
"""
from rdflib import Graph, URIRef

from rdfeval.harness import run_pair

EX = "http://example.com/"

DATA = """
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sdo:  <https://schema.org/> .
@prefix ex:   <http://example.com/> .

ex:hasPart
    sdo:rangeIncludes ex:Component , ex:Assembly ;
    sdo:domainIncludes ex:Machine .

ex:Component rdfs:label "Component" .
ex:Assembly rdfs:label "Assembly" .
ex:Bolt rdfs:label "Bolt" ; rdfs:subClassOf ex:Component .
ex:Nut rdfs:label "Nut" ; rdfs:subClassOf ex:Component .

ex:hasColour sdo:rangeIncludes ex:Colour .
ex:hasWeight rdfs:range ex:Weight .
"""

DB_DATA = """
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ex:   <http://example.com/> .
ex:Colour rdfs:label "Colour (from the union graph)" .
"""


def _graph_and_db():
    g = Graph()
    g.parse(data=DATA, format="turtle")
    db = Graph()
    db.parse(data=DB_DATA, format="turtle")
    return g, db


def two_ranges_with_subclasses():
    g, db = _graph_and_db()
    return ((URIRef(EX + "hasPart"), g, db), {})


def name_from_dataset():
    g, db = _graph_and_db()
    return ((URIRef(EX + "hasColour"), g, db), {})


def no_range_includes():
    g, db = _graph_and_db()
    return ((URIRef(EX + "hasWeight"), g, db), {})


VERDICT = run_pair(__file__, entry="get_range_includes",
                   calls=[two_ranges_with_subclasses, name_from_dataset,
                          no_range_includes])

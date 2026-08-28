"""Validation driver: get_super_profiles walks a prof:isProfileOf hierarchy.

The fixture graph is parsed from the same Turtle text on both sides, so the
store's iteration order (which the region's result order follows) is the same;
the returned ProfileHierarchyItem trees are compared field by field.
"""
from rdflib import Graph, URIRef

from rdfeval.harness import run_pair

PROFILES = """
@prefix prof: <http://www.w3.org/ns/dx/prof/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ex:   <https://example.org/> .

ex:leaf     a prof:Profile ; rdfs:label "Leaf profile" ;
            prof:isProfileOf ex:middle, ex:sibling .
ex:middle   a prof:Profile ; rdfs:label "Middle profile" ;
            prof:isProfileOf ex:root .
ex:sibling  a prof:Profile ; rdfs:label "Sibling profile" .
ex:root     a prof:Profile ; rdfs:label "Root profile" .
"""


def fixture_leaf():
    g = Graph()
    g.parse(data=PROFILES, format="turtle")
    return ((URIRef("https://example.org/leaf"), g), {})


def fixture_no_super():
    """A profile with no prof:isProfileOf statement: empty result."""
    g = Graph()
    g.parse(data=PROFILES, format="turtle")
    return ((URIRef("https://example.org/root"), g), {})


VERDICT = run_pair(__file__, entry="get_super_profiles",
                   calls=[fixture_leaf, fixture_no_super])

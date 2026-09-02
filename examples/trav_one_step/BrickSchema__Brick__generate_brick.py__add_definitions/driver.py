"""Validation driver for BrickSchema__Brick__generate_brick.py__add_definitions.

Establishes semantic equivalence of original.py and translated.ldpy by
isomorphism of the graph add_definitions() mutates -- entry=/calls= run the
function on a fresh graph for each side and compare the resulting graphs.

The function does two things: (1) reads ./bricksrc/definitions.csv (relative
to the driver's own directory -- rdfeval.check runs the driver with cwd set
to the example directory) and adds skos:definition/rdfs:seeAlso triples per
row; (2) walks every `?param rdfs:subClassOf* brick:Limit` already in the
graph and adds a generated skos:definition, UNLESS `param` already has a
brick:aliasOf -- the one-step read this stratum targets.

call_with_hierarchy() pre-populates the graph passed in with:
  - brick:Min_Limit, brick:Max_Limit rdfs:subClassOf brick:Limit, neither
    aliased -- the zero-solution case for `m{ {param} brick:aliasOf ?o }`,
    so both get a generated skos:definition;
  - brick:Alias_Limit rdfs:subClassOf brick:Limit AND brick:aliasOf
    brick:Min_Limit -- the one-solution case: the read must find it and the
    function must skip adding a definition for it;
  - brick:Setpoint rdfs:subClassOf brick:Class, neighbouring data that must
    NOT satisfy `?param rdfs:subClassOf* brick:Limit` (it isn't a Limit),
    exercised only through the class_exists lookup (a query, not this
    stratum's read, and printed rather than written to the graph).
definitions.csv covers a definition-only row, a definition+seeAlso row, and
a row with an empty definition that must add nothing.
"""
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import run_pair

BRICK = "https://brickschema.org/schema/Brick#"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"

HIERARCHY_TTL = f"""
@prefix brick: <{BRICK}> .
@prefix rdfs: <{RDFS}> .

brick:Min_Limit rdfs:subClassOf brick:Limit .
brick:Max_Limit rdfs:subClassOf brick:Limit .
brick:Alias_Limit rdfs:subClassOf brick:Limit .
brick:Alias_Limit brick:aliasOf brick:Min_Limit .
brick:Setpoint rdfs:subClassOf brick:Class .
"""


def call_with_hierarchy():
    g = Graph()
    g.parse(data=HIERARCHY_TTL, format="turtle")
    return ((g,), {})


VERDICT = run_pair(
    __file__,
    entry='add_definitions',
    calls=[call_with_hierarchy],
)

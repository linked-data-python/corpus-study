# Context shim (see meta.json): stand-in for
# `from semantic_objects.s223._generated import entities, properties` and for
# the test file's own module-level `_shacl_graph()` helper
# (lazlop/semantic_objects@243c5efd8c : tests/ingest/test_shacl_roundtrip_parity.py,
# lines 10-20), so the region executes without the real package.
#
# `semantic_objects` pulls in buildingmotif, pyshacl, pandas and a private
# `semantic-mpc-interface` git dependency (see its pyproject.toml) — not
# installable here. In the real repo, `_shacl_graph(entities.Battery)` calls
# `entities.Battery.generate_rdf_class_definition()`, a pydantic-style
# exporter that renders a NodeShape from the class's field annotations, and
# parses the result. Reproducing that exporter is out of reach; what this
# shim reproduces instead is its OUTPUT for `entities.Battery`, written by
# hand from the shape the test's own comments and assertions document:
# `s223:Battery` with a class-level `sh:or` of two independent branches
# (OutletConnectionPoint / BidirectionalConnectionPoint), each its own
# `sh:property` / `sh:qualifiedValueShape`, each qualified value shape
# further constrained by a nested `sh:node/sh:property` pinning
# `s223:hasMedium` to `s223:Constituent-Electricity`.
#
# Two decoy branches are added that the query under test must exclude: one
# with the right path but the wrong medium class, one with the right medium
# but the wrong path — plus an unrelated `s223:Pump` shape with a direct
# `sh:property` — so the check is not vacuous. `entities`/`properties` are
# empty stand-ins: `_shacl_graph` below ignores its `cls` argument entirely,
# since the region under test (the two SPARQL queries) does not depend on
# which entity was asked for, only on the graph `_shacl_graph` returns.
#
# Identical bindings for both representations (original.py and
# translated.ldpy import this same module).
from types import SimpleNamespace

from rdflib import Graph

entities = SimpleNamespace(Battery=object())
properties = SimpleNamespace()

_BATTERY_SHAPE_TTL = """
@prefix s223: <http://data.ashrae.org/standard223#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .

s223:Battery a sh:NodeShape ;
    sh:or ( [ sh:property [ sh:path s223:hasConnectionPoint ;
                             sh:qualifiedMinCount 1 ;
                             sh:qualifiedValueShape [ sh:class s223:OutletConnectionPoint ;
                                                       sh:node [ sh:property [ sh:path s223:hasMedium ;
                                                                                sh:class s223:Constituent-Electricity ] ] ] ] ]
              [ sh:property [ sh:path s223:hasConnectionPoint ;
                               sh:qualifiedMinCount 1 ;
                               sh:qualifiedValueShape [ sh:class s223:BidirectionalConnectionPoint ;
                                                         sh:node [ sh:property [ sh:path s223:hasMedium ;
                                                                                  sh:class s223:Constituent-Electricity ] ] ] ] ]
              [ sh:property [ sh:path s223:hasConnectionPoint ;
                               sh:qualifiedMinCount 1 ;
                               sh:qualifiedValueShape [ sh:class s223:DecoyConnectionPoint-WrongMedium ;
                                                         sh:node [ sh:property [ sh:path s223:hasMedium ;
                                                                                  sh:class s223:Constituent-Water ] ] ] ] ]
              [ sh:property [ sh:path s223:hasOtherPoint ;
                               sh:qualifiedMinCount 1 ;
                               sh:qualifiedValueShape [ sh:class s223:DecoyConnectionPoint-WrongPath ;
                                                         sh:node [ sh:property [ sh:path s223:hasMedium ;
                                                                                  sh:class s223:Constituent-Electricity ] ] ] ] ] ) .

s223:Pump a sh:NodeShape ;
    sh:property [ sh:path s223:hasConnectionPoint ] .
"""


def _shacl_graph(cls):
    g = Graph()
    g.bind("s223", "http://data.ashrae.org/standard223#")
    g.bind("sh", "http://www.w3.org/ns/shacl#")
    g.parse(data=_BATTERY_SHAPE_TTL, format="turtle")
    return g

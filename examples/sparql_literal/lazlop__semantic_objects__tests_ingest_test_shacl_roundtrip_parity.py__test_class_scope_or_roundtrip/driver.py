"""Validation driver for lazlop__semantic_objects__tests_ingest_test_shacl_roundtrip_parity.py__test_class_scope_or_roundtrip.

Establishes semantic equivalence of original.py and translated.ldpy.

This region reads a graph (two SPARQL queries, an ASK and a SELECT), so the
oracle is the values both versions produce, not isomorphism (design record
corpus/405). There is no fixture.ttl: `test_class_scope_or_roundtrip` takes
no argument and builds its own graph via `_shacl_graph()`, so the input
graph lives in `_context.py` (see meta.json for why) rather than in a Turtle
file passed through `fixture=`. `calls=[((), {})]` calls the entry point
with no arguments, once per side.

Repair 2026-10-31 (mutation audit). `_shacl_graph` parses the module
attribute `_context._BATTERY_SHAPE_TTL` at call time, and both sides import
the same `_context` module. Calls 1 and 2 set that attribute first (a
callable case runs once per side, before either side is called), so the
same entry point is re-run on three inputs, identical for both sides:

  call[0]  the shim's own graph, unchanged: ASK false, two targets.
  call[1]  the shim's graph plus _DECOYS: one branch per bound term of the
           SELECT, each correct except for that one term and carrying its
           own s223:Decoy-* target. Widening a term of the query (to a
           variable, or dropping its triple pattern) admits a decoy, so
           `targets` grows and the region's own assert raises. Before this
           call, dropping `sh:qualifiedMinCount ?min` stayed green: every
           branch of the shim had one.
  call[2]  the shim's graph plus a direct `s223:Battery sh:property`: the
           ASK is true and the first assert raises; the harness compares the
           AssertionError (type and message). Before this call only the
           ASK-false branch ran, so an emptied or never-matching ASK stayed
           green.
"""
import _context  # the very module both artefacts import (sys.modules)

from rdfeval.harness import run_pair

_SHIM_TTL = _context._BATTERY_SHAPE_TTL

# One decoy per bound term of the SELECT. A correct branch is:
#   [ sh:property [ sh:path s223:hasConnectionPoint ; sh:qualifiedMinCount 1 ;
#       sh:qualifiedValueShape [ sh:class T ;
#         sh:node [ sh:property [ sh:path s223:hasMedium ;
#                                 sh:class s223:Constituent-Electricity ] ] ] ] ]
_DECOYS = """
@prefix s223: <http://data.ashrae.org/standard223#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .

# In Battery's sh:xone, not its sh:or: kills widening sh:or.
s223:Battery sh:xone (
  [ sh:property [ sh:path s223:hasConnectionPoint ; sh:qualifiedMinCount 1 ;
      sh:qualifiedValueShape [ sh:class s223:Decoy-Xone ;
        sh:node [ sh:property [ sh:path s223:hasMedium ; sh:class s223:Constituent-Electricity ] ] ] ] ] ) .

# Another shape with a correct branch: kills widening the subject s223:Battery.
s223:OtherEquipment a sh:NodeShape ; sh:or (
  [ sh:property [ sh:path s223:hasConnectionPoint ; sh:qualifiedMinCount 1 ;
      sh:qualifiedValueShape [ sh:class s223:Decoy-OtherShape ;
        sh:node [ sh:property [ sh:path s223:hasMedium ; sh:class s223:Constituent-Electricity ] ] ] ] ] ) .

s223:Battery sh:or (
  # branch predicate sh:property -> sh:node
  [ sh:node [ sh:path s223:hasConnectionPoint ; sh:qualifiedMinCount 1 ;
      sh:qualifiedValueShape [ sh:class s223:Decoy-BranchPred ;
        sh:node [ sh:property [ sh:path s223:hasMedium ; sh:class s223:Constituent-Electricity ] ] ] ] ]
  # outer sh:path -> sh:name
  [ sh:property [ sh:name s223:hasConnectionPoint ; sh:qualifiedMinCount 1 ;
      sh:qualifiedValueShape [ sh:class s223:Decoy-PathPred ;
        sh:node [ sh:property [ sh:path s223:hasMedium ; sh:class s223:Constituent-Electricity ] ] ] ] ]
  # no sh:qualifiedMinCount
  [ sh:property [ sh:path s223:hasConnectionPoint ;
      sh:qualifiedValueShape [ sh:class s223:Decoy-NoMinCount ;
        sh:node [ sh:property [ sh:path s223:hasMedium ; sh:class s223:Constituent-Electricity ] ] ] ] ]
  # sh:qualifiedValueShape -> sh:node
  [ sh:property [ sh:path s223:hasConnectionPoint ; sh:qualifiedMinCount 1 ;
      sh:node [ sh:class s223:Decoy-QvsPred ;
        sh:node [ sh:property [ sh:path s223:hasMedium ; sh:class s223:Constituent-Electricity ] ] ] ] ]
  # target sh:class -> sh:datatype
  [ sh:property [ sh:path s223:hasConnectionPoint ; sh:qualifiedMinCount 1 ;
      sh:qualifiedValueShape [ sh:datatype s223:Decoy-ClassPred ;
        sh:node [ sh:property [ sh:path s223:hasMedium ; sh:class s223:Constituent-Electricity ] ] ] ] ]
  # sh:node -> sh:not
  [ sh:property [ sh:path s223:hasConnectionPoint ; sh:qualifiedMinCount 1 ;
      sh:qualifiedValueShape [ sh:class s223:Decoy-NodePred ;
        sh:not [ sh:property [ sh:path s223:hasMedium ; sh:class s223:Constituent-Electricity ] ] ] ] ]
  # nested sh:property -> sh:or
  [ sh:property [ sh:path s223:hasConnectionPoint ; sh:qualifiedMinCount 1 ;
      sh:qualifiedValueShape [ sh:class s223:Decoy-NestedPropPred ;
        sh:node [ sh:or [ sh:path s223:hasMedium ; sh:class s223:Constituent-Electricity ] ] ] ] ]
  # nested sh:path -> sh:name
  [ sh:property [ sh:path s223:hasConnectionPoint ; sh:qualifiedMinCount 1 ;
      sh:qualifiedValueShape [ sh:class s223:Decoy-NestedPathPred ;
        sh:node [ sh:property [ sh:name s223:hasMedium ; sh:class s223:Constituent-Electricity ] ] ] ] ]
  # nested path s223:hasMedium -> s223:hasRole
  [ sh:property [ sh:path s223:hasConnectionPoint ; sh:qualifiedMinCount 1 ;
      sh:qualifiedValueShape [ sh:class s223:Decoy-NestedPath ;
        sh:node [ sh:property [ sh:path s223:hasRole ; sh:class s223:Constituent-Electricity ] ] ] ] ]
  # medium sh:class -> sh:hasValue
  [ sh:property [ sh:path s223:hasConnectionPoint ; sh:qualifiedMinCount 1 ;
      sh:qualifiedValueShape [ sh:class s223:Decoy-MediumPred ;
        sh:node [ sh:property [ sh:path s223:hasMedium ; sh:hasValue s223:Constituent-Electricity ] ] ] ] ]
) .
"""

_ASK_TRUE = """
@prefix s223: <http://data.ashrae.org/standard223#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
s223:Battery sh:property [ sh:path s223:hasConnectionPoint ] .
"""


def _with(ttl):
    def case():
        _context._BATTERY_SHAPE_TTL = ttl
        return (), {}
    return case


VERDICT = run_pair(
    __file__,
    entry='test_class_scope_or_roundtrip',
    calls=[
        ((), {}),
        _with(_SHIM_TTL + _DECOYS),
        _with(_SHIM_TTL + _ASK_TRUE),
    ],
)

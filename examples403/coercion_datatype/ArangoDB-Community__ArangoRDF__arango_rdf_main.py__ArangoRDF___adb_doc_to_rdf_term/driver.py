"""Validation driver for ArangoDB-Community__ArangoRDF__arango_rdf_main.py__ArangoRDF___adb_doc_to_rdf_term.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='__adb_doc_to_rdf_term',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

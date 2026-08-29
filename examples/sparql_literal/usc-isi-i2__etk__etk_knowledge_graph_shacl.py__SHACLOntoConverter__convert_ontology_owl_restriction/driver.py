"""Validation driver for usc-isi-i2__etk__etk_knowledge_graph_shacl.py__SHACLOntoConverter__convert_ontology_owl_restriction.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='_convert_ontology_owl_restriction',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

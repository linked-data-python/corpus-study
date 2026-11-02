"""Validation driver for RDFLib__pySHACL__pyshacl_constraints_core_value_constraints.py__ClassConstraintComponent__evaluate_class_rules_sparql.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='_evaluate_class_rules_sparql',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

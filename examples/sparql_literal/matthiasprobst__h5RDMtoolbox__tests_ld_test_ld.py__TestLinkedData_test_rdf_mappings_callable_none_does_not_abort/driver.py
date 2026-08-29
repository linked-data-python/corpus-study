"""Validation driver for matthiasprobst__h5RDMtoolbox__tests_ld_test_ld.py__TestLinkedData_test_rdf_mappings_callable_none_does_not_abort.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='test_rdf_mappings_callable_none_does_not_abort',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

"""Validation driver for Blackcat-Informatics__purrdf__bindings_python_tests_rdflib_suite_vendor_test_having.py__test_having_primary_expression_var_neq_iri.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='test_having_primary_expression_var_neq_iri',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

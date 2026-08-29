"""Validation driver for CatholicOS__ontokit-api__tests_unit_test_consistency_service.py__test_no_multi_root.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='test_no_multi_root',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

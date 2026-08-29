"""Validation driver for cognitedata__neat__tests_v0_tests_unit_test_store_test_instance_diff.py__test_diff_instances.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='test_diff_instances',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

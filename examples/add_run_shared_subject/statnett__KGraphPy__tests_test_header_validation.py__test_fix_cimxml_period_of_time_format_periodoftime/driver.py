"""Validation driver for statnett__KGraphPy__tests_test_header_validation.py__test_fix_cimxml_period_of_time_format_periodoftime.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='test_fix_cimxml_period_of_time_format_periodoftime',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

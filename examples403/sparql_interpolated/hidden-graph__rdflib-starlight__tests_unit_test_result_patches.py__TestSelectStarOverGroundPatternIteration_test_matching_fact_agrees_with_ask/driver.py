"""Validation driver for hidden-graph__rdflib-starlight__tests_unit_test_result_patches.py__TestSelectStarOverGroundPatternIteration_test_matching_fact_agrees_with_ask.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='test_matching_fact_agrees_with_ask',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

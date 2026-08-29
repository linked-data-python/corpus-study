"""Validation driver for aigora-de__rdf-construct__tests_test_diff.py__TestCompareGraphs_test_hierarchy_change.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='test_hierarchy_change',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

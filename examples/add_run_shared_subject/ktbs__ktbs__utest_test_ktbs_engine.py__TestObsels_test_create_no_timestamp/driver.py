"""Validation driver for ktbs__ktbs__utest_test_ktbs_engine.py__TestObsels_test_create_no_timestamp.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='test_create_no_timestamp',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

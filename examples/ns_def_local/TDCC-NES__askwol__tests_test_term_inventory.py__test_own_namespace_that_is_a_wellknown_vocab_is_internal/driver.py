"""Validation driver for TDCC-NES__askwol__tests_test_term_inventory.py__test_own_namespace_that_is_a_wellknown_vocab_is_internal.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='test_own_namespace_that_is_a_wellknown_vocab_is_internal',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

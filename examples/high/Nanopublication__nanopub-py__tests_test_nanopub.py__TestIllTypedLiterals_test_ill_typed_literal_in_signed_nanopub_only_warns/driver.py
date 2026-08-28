"""Validation driver for Nanopublication__nanopub-py__tests_test_nanopub.py__TestIllTypedLiterals_test_ill_typed_literal_in_signed_nanopub_only_warns.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='test_ill_typed_literal_in_signed_nanopub_only_warns',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

"""Validation driver for citiususc__yatter__test_rml-language_INVERSETC-0007_test_inversetc0007.py__test_inversetc0007.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='test_inversetc0007',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

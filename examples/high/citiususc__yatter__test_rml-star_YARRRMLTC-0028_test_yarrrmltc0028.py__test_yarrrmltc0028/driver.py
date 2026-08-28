"""Validation driver for citiususc__yatter__test_rml-star_YARRRMLTC-0028_test_yarrrmltc0028.py__test_yarrrmltc0028.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='test_yarrrmltc0028',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

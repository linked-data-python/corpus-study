"""Validation driver for statnett__KGraphPy__tests_test_utilities.py__test_extract_subjects_by_object_type_literalsubject.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='test_extract_subjects_by_object_type_literalsubject',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

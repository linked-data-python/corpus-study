"""Validation driver for morph-kgc__morph-kgc__test_rml-fnml_string_functions_string_starts_endswith_test_string_start_end_with.py__test_string_starts_endswith.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='test_string_starts_endswith',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

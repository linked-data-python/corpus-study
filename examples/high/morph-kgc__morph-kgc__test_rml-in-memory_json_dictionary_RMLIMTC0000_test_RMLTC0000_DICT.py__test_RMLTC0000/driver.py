"""Validation driver for morph-kgc__morph-kgc__test_rml-in-memory_json_dictionary_RMLIMTC0000_test_RMLTC0000_DICT.py__test_RMLTC0000.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='test_RMLTC0000',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

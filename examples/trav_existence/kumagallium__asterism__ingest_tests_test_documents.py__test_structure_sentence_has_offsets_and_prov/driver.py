"""Validation driver for kumagallium__asterism__ingest_tests_test_documents.py__test_structure_sentence_has_offsets_and_prov.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='test_structure_sentence_has_offsets_and_prov',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

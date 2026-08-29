"""Validation driver for FAIRDataTeam__fdpneo-server__tests_unit_metadata_test_identifiers.py__TestReconcile_test_explicit_external_ids_preserved.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='test_explicit_external_ids_preserved',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

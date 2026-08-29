"""Validation driver for FAIRDataTeam__fdpneo-server__tests_unit_metadata_profiles_test_iri.py__test_expand_schema_refs_rewrites_placeholders_not_class_iris.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='test_expand_schema_refs_rewrites_placeholders_not_class_iris',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

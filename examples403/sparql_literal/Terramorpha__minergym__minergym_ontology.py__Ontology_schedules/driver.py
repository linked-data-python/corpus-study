"""Validation driver for Terramorpha__minergym__minergym_ontology.py__Ontology_schedules.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='schedules',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

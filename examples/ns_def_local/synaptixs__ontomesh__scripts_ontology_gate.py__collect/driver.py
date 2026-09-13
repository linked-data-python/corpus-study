"""Validation driver for synaptixs__ontomesh__scripts_ontology_gate.py__collect.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
import os
from rdfeval.harness import run_pair

_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "fixture_output")

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='collect',
    calls=[((_OUTPUT_DIR,), {})],
)

"""Validation driver for par-tec__security-ontologies__iso27001.py__parse_iso_controls.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='parse_iso_controls',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

"""Validation driver for danilipp17__thesis_code__oscin_populator.py__OntologyPopulator__populate_termination_conditions.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='_populate_termination_conditions',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

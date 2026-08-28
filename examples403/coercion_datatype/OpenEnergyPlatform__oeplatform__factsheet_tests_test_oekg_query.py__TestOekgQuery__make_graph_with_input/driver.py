"""Validation driver for OpenEnergyPlatform__oeplatform__factsheet_tests_test_oekg_query.py__TestOekgQuery__make_graph_with_input.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='_make_graph_with_input',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

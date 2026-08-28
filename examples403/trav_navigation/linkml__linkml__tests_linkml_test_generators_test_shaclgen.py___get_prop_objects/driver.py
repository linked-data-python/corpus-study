"""Validation driver for linkml__linkml__tests_linkml_test_generators_test_shaclgen.py___get_prop_objects.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='_get_prop_objects',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

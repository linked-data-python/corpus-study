"""Validation driver for eccenca__cmem-plugin-shapes__tests_test_shapes.py__test_workflow_execution_with_ignore_types.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='test_workflow_execution_with_ignore_types',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

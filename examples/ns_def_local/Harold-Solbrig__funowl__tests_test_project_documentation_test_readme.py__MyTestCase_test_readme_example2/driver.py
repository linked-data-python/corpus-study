"""Validation driver for Harold-Solbrig__funowl__tests_test_project_documentation_test_readme.py__MyTestCase_test_readme_example2.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='test_readme_example2',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

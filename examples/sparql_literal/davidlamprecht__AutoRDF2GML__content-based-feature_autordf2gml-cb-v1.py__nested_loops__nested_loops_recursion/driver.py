"""Validation driver for davidlamprecht__AutoRDF2GML__content-based-feature_autordf2gml-cb-v1.py__nested_loops__nested_loops_recursion.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='_nested_loops_recursion',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

"""Validation driver for BrickSchema__Brick__tools_compare_versions_compare_versions.py__get_tag_sets.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='get_tag_sets',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

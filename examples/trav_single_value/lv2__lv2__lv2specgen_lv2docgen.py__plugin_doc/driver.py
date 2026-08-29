"""Validation driver for lv2__lv2__lv2specgen_lv2docgen.py__plugin_doc.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='plugin_doc',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

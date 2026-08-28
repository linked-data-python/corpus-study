"""Validation driver for comp-rob2b__kindyngen__kindynsyn_ir_gen_translators_common.py__is_list.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='is_list',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

"""Validation driver for ktbs__ktbs__lib_ktbs_plugins_meth_external.py___ExternalMethod_compute_trace_description.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='compute_trace_description',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

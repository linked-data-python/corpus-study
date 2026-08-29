"""Validation driver for schemaorg__sdopythonapp__lib_pyRdfa_options.py__ProcessorGraph_add_http_context.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='add_http_context',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

"""Validation driver for JonAnderAsua__TFG-KG-RelacionesClientelares__procesSource_source_gate_cloud.py__TextToTriple_grafoaSortu.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='grafoaSortu',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

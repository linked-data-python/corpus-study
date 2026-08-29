"""Validation driver for SAWGraph__water-kg__datasets_sdwis_pws_serviceAreas_cws-ncws.py__triplify_pws_data.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='triplify_pws_data',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

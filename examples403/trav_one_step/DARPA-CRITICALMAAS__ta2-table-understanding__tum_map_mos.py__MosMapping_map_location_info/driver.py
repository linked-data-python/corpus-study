"""Validation driver for DARPA-CRITICALMAAS__ta2-table-understanding__tum_map_mos.py__MosMapping_map_location_info.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='map_location_info',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

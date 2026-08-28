"""Validation driver for SAWGraph__water-kg__datasets_groundwater_il-isgs_IL_ISGS_Aquifer-AqSystem-2ttl.py__process_aquifers_shp2ttl.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='process_aquifers_shp2ttl',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

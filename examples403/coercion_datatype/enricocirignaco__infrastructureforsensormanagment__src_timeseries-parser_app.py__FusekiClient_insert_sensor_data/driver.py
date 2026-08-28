"""Validation driver for enricocirignaco__infrastructureforsensormanagment__src_timeseries-parser_app.py__FusekiClient_insert_sensor_data.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='insert_sensor_data',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

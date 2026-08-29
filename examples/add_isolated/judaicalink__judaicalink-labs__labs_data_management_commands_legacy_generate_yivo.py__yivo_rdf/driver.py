"""Validation driver for judaicalink__judaicalink-labs__labs_data_management_commands_legacy_generate_yivo.py__yivo_rdf.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='yivo_rdf',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

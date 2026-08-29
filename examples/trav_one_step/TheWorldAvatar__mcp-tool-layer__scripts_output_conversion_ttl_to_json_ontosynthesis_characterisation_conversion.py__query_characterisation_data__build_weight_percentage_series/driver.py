"""Validation driver for TheWorldAvatar__mcp-tool-layer__scripts_output_conversion_ttl_to_json_ontosynthesis_characterisation_conversion.py__query_characterisation_data__build_weight_percentage_series.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='_build_weight_percentage_series',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

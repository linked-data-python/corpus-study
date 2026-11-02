"""Validation driver for TheWorldAvatar__mcp-tool-layer__scripts_output_conversion_ttl_to_json_ontosynthesis_step_conversion.py__query_step_details.

The region is one module-level statement: `vessel_type_result = list(...)`.
It reads the graph that the context shim parses from fixture.ttl, for the
step the shim names (Step_2), and leaves its result in a module global,
which run_pair compares (entry=None).  See fixture.ttl for what that step
and its neighbours hold: two vessels with the same type label (DISTINCT
folds them: a query without DISTINCT, or a pattern that is not anchored on
the step, gives other rows), a second type, a vessel type with no label, and
a neighbour step whose vessel type must not appear.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)

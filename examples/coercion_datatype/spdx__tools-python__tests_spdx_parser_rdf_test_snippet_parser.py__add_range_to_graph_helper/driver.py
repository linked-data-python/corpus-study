"""Validation driver for spdx__tools-python__tests_spdx_parser_rdf_test_snippet_parser.py__add_range_to_graph_helper.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='add_range_to_graph_helper',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

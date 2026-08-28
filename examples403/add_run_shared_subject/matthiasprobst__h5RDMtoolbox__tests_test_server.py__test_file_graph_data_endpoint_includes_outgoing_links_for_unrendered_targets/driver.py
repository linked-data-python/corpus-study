"""Validation driver for matthiasprobst__h5RDMtoolbox__tests_test_server.py__test_file_graph_data_endpoint_includes_outgoing_links_for_unrendered_targets.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='test_file_graph_data_endpoint_includes_outgoing_links_for_unrendered_targets',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

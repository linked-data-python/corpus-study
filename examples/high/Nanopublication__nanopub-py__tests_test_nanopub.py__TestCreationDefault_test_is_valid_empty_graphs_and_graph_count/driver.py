"""Validation driver for Nanopublication__nanopub-py__tests_test_nanopub.py__TestCreationDefault_test_is_valid_empty_graphs_and_graph_count.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='test_is_valid_empty_graphs_and_graph_count',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

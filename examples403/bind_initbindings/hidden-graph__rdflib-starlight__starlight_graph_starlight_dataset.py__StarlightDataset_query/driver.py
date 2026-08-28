"""Validation driver for hidden-graph__rdflib-starlight__starlight_graph_starlight_dataset.py__StarlightDataset_query.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='query',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

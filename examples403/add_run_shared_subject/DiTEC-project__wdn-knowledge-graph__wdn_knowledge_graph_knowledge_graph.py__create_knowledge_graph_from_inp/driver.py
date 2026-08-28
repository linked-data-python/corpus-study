"""Validation driver for DiTEC-project__wdn-knowledge-graph__wdn_knowledge_graph_knowledge_graph.py__create_knowledge_graph_from_inp.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='create_knowledge_graph_from_inp',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

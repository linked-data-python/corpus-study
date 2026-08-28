"""Validation driver for pyiron__semantikon__tests_unit_test_flowrep_dict.py__TestFunctionlessWorkflow_test_knowledge_graph_omits_workflow_process.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='test_knowledge_graph_omits_workflow_process',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

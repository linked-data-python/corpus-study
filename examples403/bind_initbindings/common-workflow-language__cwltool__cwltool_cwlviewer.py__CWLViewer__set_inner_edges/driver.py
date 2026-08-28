"""Validation driver for common-workflow-language__cwltool__cwltool_cwlviewer.py__CWLViewer__set_inner_edges.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='_set_inner_edges',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

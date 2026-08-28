"""Validation driver for matthiasprobst__h5RDMtoolbox__h5rdmtoolbox_catalog_core.py__InMemoryRDFStore__add_to_graph.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='_add_to_graph',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

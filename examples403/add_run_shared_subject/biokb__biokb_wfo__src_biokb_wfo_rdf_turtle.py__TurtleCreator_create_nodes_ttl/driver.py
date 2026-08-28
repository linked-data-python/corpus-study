"""Validation driver for biokb__biokb_wfo__src_biokb_wfo_rdf_turtle.py__TurtleCreator_create_nodes_ttl.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='create_nodes_ttl',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

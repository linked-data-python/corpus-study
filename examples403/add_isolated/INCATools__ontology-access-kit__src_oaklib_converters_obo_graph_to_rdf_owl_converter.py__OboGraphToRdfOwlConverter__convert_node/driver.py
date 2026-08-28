"""Validation driver for INCATools__ontology-access-kit__src_oaklib_converters_obo_graph_to_rdf_owl_converter.py__OboGraphToRdfOwlConverter__convert_node.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='_convert_node',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)

"""Validation driver for INCATools__ontology-access-kit__src_oaklib_converters_obo_graph_to_rdf_owl_converter.py__OboGraphToRdfOwlConverter__convert_node.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair
from context_shim import Converter, Meta, Node, PropertyTypeEnum
from rdflib import Graph


def _case(node):
    def make():
        return ((Converter(), node, Graph()), {})
    return make


CALLS = [
    # not source.type -> owl:Class, plus a plain-literal label
    _case(Node(id="obo:CL_0000000", lbl="cell", type=None, meta=None)),
    # source.type == "CLASS" (explicit), no label
    _case(Node(id="obo:CL_0000001", lbl=None, type="CLASS", meta=None)),
    # PROPERTY / OBJECT
    _case(Node(id="obo:RO_0002131", lbl="overlaps",
                type="PROPERTY", propertyType=PropertyTypeEnum.OBJECT,
                meta=None)),
    # PROPERTY / ANNOTATION
    _case(Node(id="obo:IAO_0000115", lbl=None,
                type="PROPERTY", propertyType=PropertyTypeEnum.ANNOTATION,
                meta=None)),
    # PROPERTY / DATA
    _case(Node(id="obo:hasWeight", lbl=None,
                type="PROPERTY", propertyType=PropertyTypeEnum.DATA,
                meta=None)),
    # INDIVIDUAL
    _case(Node(id="obo:individual_1", lbl="Alice",
                type="INDIVIDUAL", meta=None)),
]

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='_convert_node',
    calls=CALLS,
)

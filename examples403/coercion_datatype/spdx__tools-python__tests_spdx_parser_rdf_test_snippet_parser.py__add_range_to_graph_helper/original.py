# Extracted from spdx/tools-python@cef432adee : tests/spdx/parser/rdf/test_snippet_parser.py
# region: add_range_to_graph_helper (lines 154-161, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import RDF, BNode, Graph, Literal, URIRef
from spdx_tools.spdx.rdfschema.namespace import POINTER_NAMESPACE, SPDX_NAMESPACE

def add_range_to_graph_helper(graph, predicate_value_class_member):
    start_end_pointer = BNode()
    graph.add((start_end_pointer, RDF.type, POINTER_NAMESPACE.StartEndPointer))
    for predicate, value, pointer_class, pointer_member in predicate_value_class_member:
        pointer_node = BNode()
        graph.add((pointer_node, RDF.type, pointer_class))
        graph.add((start_end_pointer, predicate, pointer_node))
        graph.add((pointer_node, pointer_member, Literal(value)))

# Extracted from Mat-O-Lab/RDFConverter@0d81f4d1ba : rmlmapper.py
# region: find_object (lines 162-165, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import RDF, Graph, Literal, Namespace, URIRef
RR = Namespace("http://www.w3.org/ns/r2rml#")

def find_object(graph: Graph, triples_node):
    pom_node = graph.value(triples_node, RR.predicateObjectMap, any=False)
    om_node = graph.value(pom_node, RR.objectMap, any=False)
    return graph.value(om_node, RR.constant, any=False)

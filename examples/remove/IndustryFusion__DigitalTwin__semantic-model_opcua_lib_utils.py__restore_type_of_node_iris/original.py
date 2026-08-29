# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/lib/utils.py
# region: restore_type_of_node_iris (lines 717-736, stratum remove)
# licence of the source repository: see meta.json
from rdflib.namespace import RDFS, OWL, RDF
from rdflib import URIRef, Namespace, Graph, Literal, BNode

def restore_type_of_node_iris(ig: Graph, opcuans: Namespace, basens: Namespace):
    """
    Inverse of the replace_type_of_node_iris.
    This is transforming imported ontologies from the insntaceOf back to rdf:type.
    Note that this, in contrast to the replace function is applied to the imported
    ontologies in ig graph.
    """
    query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                SELECT ?s ?o WHERE {
                    ?s base:instanceOf ?o .
                }
    """
    query_result = ig.query(query, initNs={'opcua': opcuans, 'base': basens})
    for s, o in query_result:
        ig.remove((s, basens['instanceOf'], o))
        ig.add((s, RDF.type, o))

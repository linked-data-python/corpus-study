# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/lib/entity.py
# region: Entity.add_all_objects_of_type (lines 116-146, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import OWL, RDF, RDFS
from lib.utils import NGSILD, collection_to_list, calculate_array_dimensions
import logging
logger = logging.getLogger(__name__)

def add_all_objects_of_type(self, g, obj):
    if obj == RDF.nil:
        return
    if isinstance(obj, BNode):
        objects = collection_to_list(obj, g, scalar_conversion=False)
    else:
        objects = [obj]
    # Iterate over all objects in the list
    # collect all potential target nodes for NodeId references
    # after the loop, add them to the entity graph
    unique_onc = set()
    for o in objects:
        unique_onc.add(o)
        logger.info(f"Adding all potential target nodes for NodeId reference of type {o}")
        bindings = {'nodeclass': o}
        result = g.query("""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?onc ?type WHERE {
            ?nodeclass a ?type .
            FILTER NOT EXISTS {?type rdfs:subClassOf+ opcua:BaseNodeClass . }
            ?onc a ?type .
            FILTER(?nodeclass != ?onc) .
        }""", initBindings=bindings, initNs={'base': self.basens, 'opcua': self.opcuans})
        # Collect all unique rows in a set to avoid duplicates

        for row in result:
            unique_onc.add(row.onc)
        # Add all triples for each unique onc after collecting
    for onc in unique_onc:
        for (s, p, o) in g.triples((onc, None, None)):
            self.e.add((s, p, o))

# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/lib/utils.py
# region: RdfUtils.generate_node_id (lines 954-963, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import URIRef, Namespace, Graph, Literal, BNode

def generate_node_id(self, graph, rootentity, node, id):
    node_id = next(graph.objects(node, self.basens['hasNodeId']), 'unknown')
    idtype = next(graph.objects(node, self.basens['hasIdentifierType']), 'unknown')
    rootns = next(graph.objects(rootentity, self.basens['hasNamespace']), 'unknown')
    rootnsuri = next(graph.objects(rootns, self.basens['hasUri']), 'unknown')
    ns = next(graph.objects(node, self.basens['hasNamespace']), 'unknown')
    nsuri = next(graph.objects(ns, self.basens['hasUri']), 'unknown')
    nsurins = Namespace(nsuri)
    result = nodeId_to_iri(nsurins, self.basens, node_id, idtype, id, is_entityns=(str(nsuri) == str(rootnsuri)))
    return result

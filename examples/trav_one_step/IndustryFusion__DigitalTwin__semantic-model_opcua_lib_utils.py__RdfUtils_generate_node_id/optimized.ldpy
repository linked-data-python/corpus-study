# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/lib/utils.py
# region: RdfUtils.generate_node_id (lines 954-963, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import URIRef, Namespace, Graph, Literal, BNode
from rdfutils_context import nodeId_to_iri

def generate_node_id(self, graph, rootentity, node, id):
    def value(subject, name):
        return next(graph.objects(subject, self.basens[name]), 'unknown')

    rootnsuri = value(value(rootentity, 'hasNamespace'), 'hasUri')
    nsuri = value(value(node, 'hasNamespace'), 'hasUri')
    return nodeId_to_iri(
        Namespace(nsuri), self.basens, value(node, 'hasNodeId'), value(node, 'hasIdentifierType'),
        id, is_entityns=str(nsuri) == str(rootnsuri),
    )

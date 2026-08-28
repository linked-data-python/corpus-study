# Extracted from dtai-kg/SCOOP@40c6fc0420 : SCOOP/shape_integration_priority_r.py
# region: ShapeIntegrationPriorityR.extractSubgraph (lines 398-409, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, Literal, BNode

def extractSubgraph(self, shape: Graph, identifier, visited_nodes=None):
    # Extract the subgraph starting from the given identifier
    if visited_nodes is None:
        visited_nodes = set()
    subgraph = Graph()
    for s, p, o in shape.triples((identifier, None, None)):
        subgraph += shape.triples((s,p,o))
        if o not in visited_nodes:
            visited_nodes.add(o)
            subgraph += shape.triples((o, None, None))
            subgraph += self.extractSubgraph(shape, o, visited_nodes)
    return subgraph

# Extracted from RDFLib/prez@421ee0a9fe : prez/services/query_generation/shacl.py
# region: NodeShape.from_graph (lines 107-131, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib.namespace import RDF, SH
from prez.reference_data.prez_ns import ONT, SHEXT

def from_graph(self):  # TODO this can be a SPARQL select against the system graph.
    self.bnode_depth = next(
        self.graph.objects(self.uri, SHEXT["bnode-depth"]), None
    )
    self.targetNode = next(self.graph.objects(self.uri, SH.targetNode), None)
    self.targetClasses = list(self.graph.objects(self.uri, SH.targetClass))
    self.propertyShapesURIs = list(self.graph.objects(self.uri, SH.property))
    self.target = next(self.graph.objects(self.uri, SH.target), None)
    self.rules = list(self.graph.objects(self.uri, SH.rule))
    self.propertyShapes = [
        PropertyShape(
            uri=ps_uri,
            graph=self.graph,
            kind=self.kind,
            focus_node=self.focus_node,
            path_nodes=self.path_nodes,
            shape_number=i,
        )
        for i, ps_uri in enumerate(self.propertyShapesURIs)
    ]
    self.hierarchy_level = next(
        self.graph.objects(self.uri, ONT.hierarchyLevel), None
    )
    if not self.hierarchy_level and self.kind == "endpoint":
        raise ValueError("No hierarchy level found")

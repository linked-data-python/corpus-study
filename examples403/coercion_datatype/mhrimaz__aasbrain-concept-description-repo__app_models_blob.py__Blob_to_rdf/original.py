# Extracted from mhrimaz/aasbrain-concept-description-repo@46ae59a87e : app/models/blob.py
# region: Blob.to_rdf (lines 45-70, stratum coercion_datatype)
# licence of the source repository: see meta.json
import rdflib
from rdflib import RDF
from app.models.aas_namespace import AASNameSpace

def to_rdf(
    self,
    graph: rdflib.Graph = None,
    parent_node: rdflib.IdentifiedNode = None,
    prefix_uri: str = "",
    base_uri: str = "",
    id_strategy: str = "",
) -> (rdflib.Graph, rdflib.IdentifiedNode):
    created_graph, created_node = super().to_rdf(graph, parent_node, prefix_uri, base_uri, id_strategy)
    created_graph.add((created_node, RDF.type, AASNameSpace.AAS["Blob"]))
    if self.value != None:
        created_graph.add(
            (
                created_node,
                AASNameSpace.AAS["Blob/value"],
                rdflib.Literal(self.value, datatype=rdflib.XSD.base64Binary),
            )
        )
    created_graph.add(
        (
            created_node,
            AASNameSpace.AAS["Blob/contentType"],
            rdflib.Literal(self.contentType),
        )
    )
    return created_graph, created_node

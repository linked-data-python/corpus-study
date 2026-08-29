# Extracted from mhrimaz/aasbrain-concept-description-repo@46ae59a87e : app/models/concept_description.py
# region: ConceptDescription.to_rdf (lines 44-75, stratum add_isolated)
# licence of the source repository: see meta.json
import rdflib
from app.models.aas_namespace import AASNameSpace
from app.models.has_data_specification import HasDataSpecification
from app.models.identifiable import Identifiable
from app.models import base_64_url_encode, url_encode

def to_rdf(
    self,
    graph: rdflib.Graph = None,
    parent_node: rdflib.IdentifiedNode = None,
    prefix_uri: str = "",
    base_uri: str = "",
    id_strategy: str = "",
) -> (rdflib.Graph, rdflib.IdentifiedNode):
    if graph == None:
        graph = rdflib.Graph()
        graph.bind("aas", AASNameSpace.AAS)
        graph.bind("myaas", base_uri)

    if id_strategy == "base64-url-encode":
        node = rdflib.URIRef(f"{base_uri}{base_64_url_encode(self.id)}")
    else:
        node = rdflib.URIRef(f"{base_uri}{url_encode(self.id)}")
    graph.add((node, rdflib.RDF.type, AASNameSpace.AAS["ConceptDescription"]))

    # Identifiable
    # TODO: find a way to refactor
    Identifiable.append_as_rdf(self, graph, node)

    # HasDataSpecification
    HasDataSpecification.append_as_rdf(self, graph, node)

    if self.isCaseOf and len(self.isCaseOf) > 0:
        for idx, is_case in enumerate(self.isCaseOf):
            _, created_node = is_case.to_rdf(graph, node, prefix_uri, base_uri, id_strategy)
            graph.add((created_node, AASNameSpace.AAS["index"], rdflib.Literal(idx)))
            graph.add((node, AASNameSpace.AAS["ConceptDescription/isCaseOf"], created_node))
    return graph, node

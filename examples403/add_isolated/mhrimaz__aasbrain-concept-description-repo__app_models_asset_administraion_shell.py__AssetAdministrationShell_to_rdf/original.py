# Extracted from mhrimaz/aasbrain-concept-description-repo@46ae59a87e : app/models/asset_administraion_shell.py
# region: AssetAdministrationShell.to_rdf (lines 45-91, stratum add_isolated)
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

    graph.add((node, rdflib.RDF.type, AASNameSpace.AAS["AssetAdministrationShell"]))

    # Identifiable
    # TODO: find a way to refactor
    Identifiable.append_as_rdf(self, graph, node)

    # HasDataSpecification
    HasDataSpecification.append_as_rdf(self, graph, node)

    if self.derivedFrom:
        _, created_node = self.derivedFrom.to_rdf(
            graph, node, base_uri=base_uri, prefix_uri=prefix_uri, id_strategy=id_strategy
        )
        graph.add((node, AASNameSpace.AAS["AssetAdministrationShell/derivedFrom"], created_node))

    _, created_asset_info_node = self.assetInformation.to_rdf(
        graph, node, base_uri=base_uri, prefix_uri=prefix_uri, id_strategy=id_strategy
    )
    graph.add((node, AASNameSpace.AAS["AssetAdministrationShell/assetInformation"], created_asset_info_node))

    if self.submodels and len(self.submodels) > 0:
        for idx, submodel_ref in enumerate(self.submodels):
            _, created_ref_node = submodel_ref.to_rdf(
                graph, node, base_uri=base_uri, prefix_uri=prefix_uri, id_strategy=id_strategy
            )
            graph.add((created_ref_node, AASNameSpace.AAS["index"], rdflib.Literal(idx)))
            graph.add((node, AASNameSpace.AAS["AssetAdministrationShell/submodels"], created_ref_node))

    return graph, node

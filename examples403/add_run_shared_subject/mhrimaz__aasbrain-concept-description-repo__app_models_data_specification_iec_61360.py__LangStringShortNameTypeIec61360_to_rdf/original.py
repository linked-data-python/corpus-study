# Extracted from mhrimaz/aasbrain-concept-description-repo@46ae59a87e : app/models/data_specification_iec_61360.py
# region: LangStringShortNameTypeIec61360.to_rdf (lines 71-87, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
import rdflib
from app.models.aas_namespace import AASNameSpace

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

    node = rdflib.BNode()
    graph.add((node, rdflib.RDF.type, AASNameSpace.AAS["LangStringShortNameTypeIec61360"]))
    graph.add((node, AASNameSpace.AAS["AbstractLangString/language"], rdflib.Literal(self.language)))
    graph.add((node, AASNameSpace.AAS["AbstractLangString/text"], rdflib.Literal(self.text)))
    return graph, node

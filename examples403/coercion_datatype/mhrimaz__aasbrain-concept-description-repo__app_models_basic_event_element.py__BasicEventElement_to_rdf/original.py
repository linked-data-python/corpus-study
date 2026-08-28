# Extracted from mhrimaz/aasbrain-concept-description-repo@46ae59a87e : app/models/basic_event_element.py
# region: BasicEventElement.to_rdf (lines 72-120, stratum coercion_datatype)
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
    created_graph.add((created_node, RDF.type, AASNameSpace.AAS["BasicEventElement"]))

    _, created_observed_node = self.observed.to_rdf(created_graph, created_node)
    created_graph.add((created_node, AASNameSpace.AAS["BasicEventElement/observed"], created_observed_node))
    created_graph.add(
        (
            created_node,
            AASNameSpace.AAS["BasicEventElement/direction"],
            AASNameSpace.AAS[f"Direction/{self.direction.name}"],
        )
    )
    created_graph.add(
        (
            created_node,
            AASNameSpace.AAS["BasicEventElement/state"],
            AASNameSpace.AAS[f"StateOfEvent/{self.state.name}"],
        )
    )
    if self.messageTopic:
        _, created_message_broker_node = self.messageBroker.to_rdf(created_graph, created_node)
        created_graph.add(
            (created_node, AASNameSpace.AAS["BasicEventElement/messageBroker"], created_message_broker_node)
        )
    if self.messageBroker:
        created_graph.add(
            (created_node, AASNameSpace.AAS["BasicEventElement/messageTopic"], rdflib.Literal(self.messageTopic))
        )
    if self.lastUpdate:
        created_graph.add(
            (created_node, AASNameSpace.AAS["BasicEventElement/lastUpdate"], rdflib.Literal(self.lastUpdate))
        )
    if self.minInterval:
        created_graph.add(
            (created_node, AASNameSpace.AAS["BasicEventElement/minInterval"], rdflib.Literal(self.minInterval))
        )
    if self.maxInterval:
        created_graph.add(
            (created_node, AASNameSpace.AAS["BasicEventElement/maxInterval"], rdflib.Literal(self.maxInterval))
        )
    return created_graph, created_node

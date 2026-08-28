# Extracted from mhrimaz/aasbrain-concept-description-repo@46ae59a87e : app/models/qualifier.py
# region: Qualifier.append_as_rdf (lines 46-71, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
import rdflib
from app.models.aas_namespace import AASNameSpace
from app.models.has_semantics import HasSemantics

@staticmethod
def append_as_rdf(instance: "Qualifier", graph: rdflib.Graph, parent_node: rdflib.IdentifiedNode):
    # HasSemantics
    HasSemantics.append_as_rdf(instance, graph, parent_node)

    if instance.kind:
        graph.add(
            (
                parent_node,
                AASNameSpace.AAS["Qualifier/kind"],
                AASNameSpace.AAS[f"QualifierKind/{instance.kind.value}"],
            )
        )
    graph.add((parent_node, AASNameSpace.AAS["Qualifier/type"], rdflib.Literal(instance.type)))
    graph.add(
        (
            parent_node,
            AASNameSpace.AAS["Qualifier/valueType"],
            AASNameSpace.AAS[f"DataTypeDefXsd/{instance.valueType.name}"],
        )
    )
    if instance.value:
        graph.add((parent_node, AASNameSpace.AAS["Qualifier/value"], rdflib.Literal(instance.value)))
    if instance.valueId:
        _, created_node = instance.valueId.to_rdf(graph, parent_node)
        graph.add((parent_node, AASNameSpace.AAS["Qualifier/valueId"], created_node))

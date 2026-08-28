# Extracted from mhrimaz/aasbrain-concept-description-repo@46ae59a87e : app/models/submodel_element_list.py
# region: SubmodelElementList.from_rdf (lines 122-187, stratum trav_single_value)
# licence of the source repository: see meta.json
import rdflib
from app.models.aas_namespace import AASNameSpace
from app.models.data_type_def_xsd import DataTypeDefXsd
from app.models.reference import Reference
from app.models.submodel_element import SubmodelElement

@staticmethod
def from_rdf(graph: rdflib.Graph, subject: rdflib.IdentifiedNode) -> "SubmodelElementList":
    submodel_element = SubmodelElement.from_rdf(graph, subject)
    order_relevant_value = None
    order_relevant_ref: rdflib.Literal = next(
        graph.objects(subject=subject, predicate=AASNameSpace.AAS["SubmodelElementList/orderRelevant"]),
        None,
    )
    if order_relevant_ref:
        order_relevant_value = order_relevant_ref.value

    semantic_id_list_element_value = None
    semantic_id_list_element_ref: rdflib.Literal = next(
        graph.objects(subject=subject, predicate=AASNameSpace.AAS["SubmodelElementList/semanticIdListElement"]),
        None,
    )
    if semantic_id_list_element_ref:
        semantic_id_list_element_value = Reference.from_rdf(graph, semantic_id_list_element_ref)
    type_value_list_element_value = None
    type_value_list_element_ref: rdflib.URIRef = next(
        graph.objects(subject=subject, predicate=AASNameSpace.AAS["SubmodelElementList/typeValueListElement"]),
        None,
    )
    if type_value_list_element_ref:
        type_value_list_element_value = AasSubmodelElements[
            type_value_list_element_ref[type_value_list_element_ref.rfind("/") + 1 :]
        ]

    value_type_list_element_value = None
    value_type_list_element_ref: rdflib.URIRef = next(
        graph.objects(subject=subject, predicate=AASNameSpace.AAS["SubmodelElementList/valueTypeListElement"]),
        None,
    )
    if value_type_list_element_ref:
        value_type_list_element_value = DataTypeDefXsd[
            value_type_list_element_ref[value_type_list_element_ref.rfind("/") + 1 :]
        ]

    value_value = []
    from app.models.util import from_unknown_rdf

    for submodel_element_uriref in graph.objects(
        subject=subject, predicate=AASNameSpace.AAS["SubmodelElementList/value"]
    ):
        element = from_unknown_rdf(graph, submodel_element_uriref)
        value_value.append(element)

    if len(value_value) == 0:
        value_value = None

    return SubmodelElementList(
        orderRelevant=order_relevant_value,
        semanticIdListElement=semantic_id_list_element_value,
        typeValueListElement=type_value_list_element_value,
        valueTypeListElement=value_type_list_element_value,
        value=value_value,
        qualifiers=submodel_element.qualifiers,
        category=submodel_element.category,
        idShort=submodel_element.idShort,
        displayName=submodel_element.displayName,
        description=submodel_element.description,
        extensions=submodel_element.extensions,
        semanticId=submodel_element.semanticId,
        supplementalSemanticIds=submodel_element.supplementalSemanticIds,
        embeddedDataSpecifications=submodel_element.embeddedDataSpecifications,
    )

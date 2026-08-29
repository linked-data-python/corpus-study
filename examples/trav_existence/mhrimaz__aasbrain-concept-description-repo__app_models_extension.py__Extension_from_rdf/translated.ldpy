# Extracted from mhrimaz/aasbrain-concept-description-repo@46ae59a87e : app/models/extension.py
# region: Extension.from_rdf (lines 79-122, stratum trav_existence)
# licence of the source repository: see meta.json
import rdflib
from app.models.aas_namespace import AASNameSpace
from app.models.data_type_def_xsd import DataTypeDefXsd
from app.models.has_semantics import HasSemantics
from app.models.reference import Reference

@staticmethod
def from_rdf(graph: rdflib.Graph, subject: rdflib.IdentifiedNode):
    # HasSemantics
    # Not oop!
    hasSemantics = HasSemantics.from_rdf(graph, subject)

    name: rdflib.Literal = next(
        graph.objects(subject=subject, predicate=AASNameSpace.AAS["Extension/name"]),
        None,
    )
    value_type_ref: rdflib.URIRef = next(
        graph.objects(subject=subject, predicate=AASNameSpace.AAS["Extension/valueType"]),
        None,
    )
    value_type = None
    if value_type_ref:
        value_type = DataTypeDefXsd[value_type_ref[value_type_ref.rfind("/") + 1 :]]

    value = None
    value_ref: rdflib.Literal = next(
        graph.objects(subject=subject, predicate=AASNameSpace.AAS["Extension/value"]),
        None,
    )
    if value_ref:
        value = value_ref.value

    refersTo_ref: rdflib.URIRef = next(
        graph.objects(subject=subject, predicate=AASNameSpace.AAS["Extension/refersTo"]),
        None,
    )
    refersTo = []
    if refersTo_ref in graph.objects(subject=subject, predicate=AASNameSpace.AAS["Extension/refersTo"]):
        refersTo.append(Reference.from_rdf(graph, refersTo_ref))

    if len(refersTo) == 0:
        refersTo = None
    return Extension.model_construct(
        name=name.value,
        valueType=value_type,
        value=value,
        refersTo=refersTo,
        supplementalSemanticIds=hasSemantics.supplementalSemanticIds,
        semanticId=hasSemantics.semanticId,
    )

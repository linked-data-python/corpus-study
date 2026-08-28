# Extracted from mhrimaz/aasbrain-concept-description-repo@46ae59a87e : app/models/specific_asset_id.py
# region: SpecificAssetId.from_rdf (lines 72-104, stratum trav_single_value)
# licence of the source repository: see meta.json
import rdflib
from app.models.aas_namespace import AASNameSpace
from app.models.has_semantics import HasSemantics
from app.models.reference import Reference

@staticmethod
def from_rdf(graph: rdflib.Graph, subject: rdflib.IdentifiedNode):
    name_value = None

    name_ref: rdflib.Literal = next(
        graph.objects(subject=subject, predicate=AASNameSpace.AAS["SpecificAssetId/name"]), None
    )
    if name_ref:
        name_value = name_ref.value

    value_ref: rdflib.Literal = next(
        graph.objects(subject=subject, predicate=AASNameSpace.AAS["SpecificAssetId/value"]), None
    )
    value_value = None
    if value_ref:
        value_value = value_ref.value

    external_subject_id_value = None
    external_subject_id_ref: rdflib.URIRef = next(
        graph.objects(subject=subject, predicate=AASNameSpace.AAS["SpecificAssetId/externalSubjectId"]), None
    )
    if external_subject_id_ref:
        external_subject_id_value = Reference.from_rdf(graph, external_subject_id_ref)

    # HasSemantics
    hasSemantics = HasSemantics.from_rdf(graph, subject)
    return SpecificAssetId(
        name=name_value,
        value=value_value,
        externalSubjectId=external_subject_id_value,
        semanticId=hasSemantics.semanticId,
        supplementalSemanticIds=hasSemantics.supplementalSemanticIds,
    )

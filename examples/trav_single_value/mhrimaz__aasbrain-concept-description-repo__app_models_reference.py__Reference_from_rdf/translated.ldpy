# Extracted from mhrimaz/aasbrain-concept-description-repo@46ae59a87e : app/models/reference.py
# region: Reference.from_rdf (lines 66-92, stratum trav_single_value)
# licence of the source repository: see meta.json
import rdflib
from app.models.aas_namespace import AASNameSpace
from app.models.key import Key, SubmodelKey
from app.models.reference_types import ReferenceTypes

@staticmethod
def from_rdf(graph: rdflib.Graph, subject: rdflib.IdentifiedNode):
    payload = {}
    key_type: rdflib.URIRef = next(
        graph.objects(subject=subject, predicate=AASNameSpace.AAS["Reference/type"]),
        None,
    )
    payload["type"] = key_type[key_type.rfind("/") + 1 :]

    keys_content = graph.objects(subject=subject, predicate=AASNameSpace.AAS["Reference/keys"])
    keys = {}
    for key in keys_content:
        created_key: Key = Key.from_rdf(graph, key)
        key_index_ref: rdflib.Literal = next(graph.objects(subject=key, predicate=AASNameSpace.AAS["index"]), None)
        keys[key_index_ref.value] = created_key
        # TODO: make sure about the order
    referred_semantic_id: rdflib.IdentifiedNode = next(
        graph.objects(subject=subject, predicate=AASNameSpace.AAS["Reference/referredSemanticId"]),
        None,
    )
    referred_semantic_id_created = None
    if referred_semantic_id:
        referred_semantic_id_created = Reference.from_rdf(graph, referred_semantic_id)
    payload["keys"] = [keys[i] for i in range(len(keys.items()))]
    return Reference.model_construct(
        type=ReferenceTypes(payload["type"]), keys=payload["keys"], referredSemanticId=referred_semantic_id_created
    )

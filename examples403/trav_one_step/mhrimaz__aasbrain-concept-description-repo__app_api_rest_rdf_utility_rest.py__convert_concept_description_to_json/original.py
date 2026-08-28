# Extracted from mhrimaz/aasbrain-concept-description-repo@46ae59a87e : app/api/rest/rdf_utility_rest.py
# region: convert_concept_description_to_json (lines 89-107, stratum trav_one_step)
# licence of the source repository: see meta.json
import json
import rdflib
import fastapi
from app.models.aas_namespace import AASNameSpace
from app.models.concept_description import ConceptDescription
from fastapi.responses import JSONResponse
router = APIRouter()

@router.post("/concept-description:rdftojson", tags=["RDF"])
async def convert_concept_description_to_json(
    concept: str = fastapi.Body(
        ...,
        media_type="text/turtle",
        examples=[
            '@prefix aas: <https://admin-shell.io/aas/3/0/> . \n\n<TXlDb25jZXB0> a aas:ConceptDescription ; \n    <https://admin-shell.io/aas/3/0/Identifiable/id> "MyConcept" .'
        ],
    ),
):
    graph = rdflib.Graph().parse(data=concept, format="turtle")
    print(graph.serialize(format="turtle"))
    # Only consider the instance of ConceptDescription.
    target: rdflib.URIRef = next(
        graph.subjects(predicate=rdflib.Graph, object=AASNameSpace.AAS["ConceptDescription"]), None
    )
    payload = ConceptDescription.from_rdf(graph, target)
    result = payload.model_dump_json(exclude_none=True)
    return JSONResponse(json.loads(result), status_code=200)

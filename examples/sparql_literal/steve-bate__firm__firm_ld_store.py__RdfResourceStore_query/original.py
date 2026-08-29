# Extracted from steve-bate/firm@4ef546a441 : firm/ld/store.py
# region: RdfResourceStore.query (lines 85-115, stratum sparql_literal)
# licence of the source repository: see meta.json
import rdflib
from pyld import jsonld
from firm.core.interfaces import JSONObject, QueryCriteria, ResourceStore
from firm.ld.jsonld_utils import (
    JSONLD_CONTEXT,
    httpx_document_loader,
    jsonld_to_graph,
    subject_to_jsonld,
)

    async def query(self, criteria: QueryCriteria) -> list[JSONObject]:
        # TODO Make prefixes configurable
        query = """
PREFIX firm: <https://firm.stevebate.dev#>
Select ?subject
Where {
"""
        expanded_criteria = jsonld.expand(
            criteria,
            dict(
                expandContext=JSONLD_CONTEXT["@context"],
                documentLoader=httpx_document_loader,
            ),
        )
        for pred, (obj,) in expanded_criteria[0].items():
            if "@value" in obj:
                if isinstance(obj["@value"], str):
                    value = obj["@value"]
                    obj = f'"{value}"'
            elif "@id" in obj:
                obj = f"<{obj['@id']}>"
            if pred == "@type":
                pred = rdflib.RDF.type
            query += f"  ?subject {pred if pred.startswith("firm:") else f'<{pred}>'} {obj} .\n"
        query += "}"
        matches: list[JSONObject] = []
        for result in self.graph.query(query):
            match = await self.get(str(result[0]))
            if match:
                matches.append(match)
        return matches

# Extracted from cognitedata/neat@4042d3e96d : cognite/neat/_v0/core/_data_model/importers/_rdf/_shared.py
# region: parse_concepts (lines 21-86, stratum sparql_interpolated)
# licence of the source repository: see meta.json
from typing import Any, Literal, cast
from rdflib import BNode, Graph, Namespace, URIRef
from rdflib.plugins.sparql import prepareQuery
from rdflib.query import ResultRow
from cognite.neat._v0.core._constants import cognite_prefixes
from cognite.neat._v0.core._issues._base import IssueList
from cognite.neat._v0.core._issues.errors._general import NeatValueError
from cognite.neat._v0.core._issues.warnings._resources import (
    ResourceRedefinedWarning,
    ResourceRetrievalWarning,
)

def parse_concepts(
    graph: Graph, query: str, parameters: set, language: str, issue_list: IssueList
) -> tuple[dict, IssueList]:
    """Parse concepts from graph

    Args:
        graph: Graph containing concept definitions
        query: SPARQL query to use for parsing concepts
        parameters: Set of parameters to extract from the query results
        language: Language to use for parsing, by default "en"
        issue_list: List to collect issues during parsing

    Returns:
        Dataframe containing owl classes
    """

    concepts: dict[str, dict] = {}

    query = prepareQuery(query.format(language=language), initNs={k: v for k, v in graph.namespaces()})
    prefixes = cognite_prefixes()

    for raw in graph.query(query):
        res: dict = convert_rdflib_content(
            cast(ResultRow, raw).asdict(), uri_handling="as-concept-entity", prefixes=prefixes
        )
        res = {key: res.get(key, None) for key in parameters}

        # Safeguarding against incomplete semantic definitions
        if res["implements"] and isinstance(res["implements"], BNode):
            issue_list.append(
                ResourceRetrievalWarning(
                    res["concept"],
                    "implements",
                    error=("Unable to determine concept that is being implemented"),
                )
            )
            continue

        # sanitize the concept and implements
        res["concept"] = sanitize_entity(res["concept"])
        res["implements"] = sanitize_entity(res["implements"]) if res["implements"] else None

        concept_id = res["concept"]

        if concept_id not in concepts:
            concepts[concept_id] = res
        else:
            # Handling implements
            if concepts[concept_id]["implements"] and isinstance(concepts[concept_id]["implements"], list):
                if res["implements"] and res["implements"] not in concepts[concept_id]["implements"]:
                    concepts[concept_id]["implements"].append(res["implements"])

            elif concepts[concept_id]["implements"] and isinstance(concepts[concept_id]["implements"], str):
                concepts[concept_id]["implements"] = [concepts[concept_id]["implements"]]

                if res["implements"] and res["implements"] not in concepts[concept_id]["implements"]:
                    concepts[concept_id]["implements"].append(res["implements"])
            elif res["implements"]:
                concepts[concept_id]["implements"] = [res["implements"]]

            handle_meta("concept", concepts, concept_id, res, "name", issue_list)
            handle_meta("concept", concepts, concept_id, res, "description", issue_list)
    if not concepts:
        issue_list.append(NeatValueError("Unable to parse concepts"))

    return concepts, issue_list

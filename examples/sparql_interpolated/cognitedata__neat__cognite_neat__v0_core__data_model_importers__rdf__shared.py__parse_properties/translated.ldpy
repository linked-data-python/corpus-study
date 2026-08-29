# Extracted from cognitedata/neat@4042d3e96d : cognite/neat/_v0/core/_data_model/importers/_rdf/_shared.py
# region: parse_properties (lines 89-172, stratum sparql_interpolated)
# licence of the source repository: see meta.json
from typing import Any, Literal, cast
from urllib.parse import quote
from rdflib import BNode, Graph, Namespace, URIRef
from rdflib.plugins.sparql import prepareQuery
from rdflib.query import ResultRow
# The five imports below come from cognite.neat._v0.core.* upstream, a
# third-party package not installed here; neat_shared_context reproduces
# them (see meta.json / that module's own header for what and why).
from neat_shared_context import cognite_prefixes
from neat_shared_context import Unknown
from neat_shared_context import IssueList
from neat_shared_context import NeatValueError
from neat_shared_context import (
    ResourceRedefinedWarning,
    ResourceRetrievalWarning,
)
# convert_rdflib_content, sanitize_entity and handle_meta are parse_properties'
# own module-level siblings in upstream's _shared.py (not extracted with the
# region, since only parse_properties itself was); neat_shared_context
# reproduces them too, verbatim, next to their real transitive dependencies.
from neat_shared_context import convert_rdflib_content, sanitize_entity, handle_meta

def parse_properties(
    graph: Graph, query: str, parameters: set, language: str, issue_list: IssueList
) -> tuple[dict, IssueList]:
    """Parse properties from graph

    Args:
        graph: Graph containing property definitions
        query: SPARQL query to use for parsing properties
        parameters: Set of parameters to extract from the query results
        language: Language to use for parsing, by default "en"
        issue_list: List to collect issues during parsing

    Returns:
        Dataframe containing owl classes
    """

    properties: dict[str, dict] = {}

    query = prepareQuery(query.format(language=language), initNs={k: v for k, v in graph.namespaces()})
    prefixes = cognite_prefixes()

    for raw in graph.query(query):
        res: dict = convert_rdflib_content(
            cast(ResultRow, raw).asdict(), uri_handling="as-concept-entity", prefixes=prefixes
        )
        res = {key: res.get(key, None) for key in parameters}

        # Quote the concept id to ensure it is web-safe
        res["property_"] = quote(res["property_"], safe="")
        property_id = res["property_"]

        # Skip Bnode
        if isinstance(res["concept"], BNode):
            issue_list.append(
                ResourceRetrievalWarning(
                    property_id,
                    "property",
                    error="Cannot determine concept of property as it is a blank node",
                )
            )
            continue

        # Skip Bnode
        if isinstance(res["value_type"], BNode):
            issue_list.append(
                ResourceRetrievalWarning(
                    property_id,
                    "property",
                    error="Unable to determine value type of property as it is a blank node",
                )
            )
            continue

        # Quote the concept and value_type if they exist if not signal neat that they are not available
        res["concept"] = sanitize_entity(res["concept"]) if res["concept"] else str(Unknown)
        res["value_type"] = sanitize_entity(res["value_type"]) if res["value_type"] else str(Unknown)

        id_ = f"{res['concept']}.{res['property_']}"

        if id_ not in properties:
            properties[id_] = res
            properties[id_]["value_type"] = [properties[id_]["value_type"]]
        else:
            handle_meta("property", properties, id_, res, "name", issue_list)
            handle_meta(
                "property",
                properties,
                id_,
                res,
                "description",
                issue_list,
            )

            # Handling multi-value types
            if res["value_type"] not in properties[id_]["value_type"]:
                properties[id_]["value_type"].append(res["value_type"])

    for prop in properties.values():
        prop["value_type"] = ", ".join(prop["value_type"])

    if not properties:
        issue_list.append(NeatValueError("Unable to parse properties"))

    return properties, issue_list

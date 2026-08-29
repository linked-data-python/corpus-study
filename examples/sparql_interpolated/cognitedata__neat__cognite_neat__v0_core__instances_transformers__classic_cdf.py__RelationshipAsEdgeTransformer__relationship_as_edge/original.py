# Extracted from cognitedata/neat@4042d3e96d : cognite/neat/_v0/core/_instances/transformers/_classic_cdf.py
# region: RelationshipAsEdgeTransformer._relationship_as_edge (lines 424-458, stratum sparql_interpolated)
# licence of the source repository: see meta.json
import urllib.parse
import warnings
from collections.abc import Callable, Iterable, Iterator
from typing import cast
from rdflib import RDF, Graph, Literal, Namespace, URIRef
from cognite.neat._v0.core._issues.warnings import ResourceNotFoundWarning
from cognite.neat._v0.core._utils.rdf_ import (
    Triple,
    add_triples_in_batch,
    get_namespace,
    remove_instance_ids_in_batch,
    remove_namespace_from_uri,
)

def _relationship_as_edge(
    self,
    graph: Graph,
    relationship_id: URIRef,
    source_type: str,
    target_type: str,
    lookup_entity_with_external_id: Callable[[str, str], URIRef],
) -> list[Triple]:
    relationship_triples = cast(list[Triple], list(graph.query(f"DESCRIBE <{relationship_id}>")))
    object_by_predicates = cast(
        dict[str, URIRef | Literal],
        {remove_namespace_from_uri(row[1]): row[2] for row in relationship_triples if row[1] != RDF.type},
    )
    source_external_id = cast(URIRef, object_by_predicates["sourceExternalId"])
    target_source_id = cast(URIRef, object_by_predicates["targetExternalId"])
    try:
        source_id = lookup_entity_with_external_id(source_type, source_external_id)
    except ValueError:
        warnings.warn(
            ResourceNotFoundWarning(source_external_id, "class", str(relationship_id), "class"), stacklevel=2
        )
        return []
    try:
        target_id = lookup_entity_with_external_id(target_type, target_source_id)
    except ValueError:
        warnings.warn(
            ResourceNotFoundWarning(target_source_id, "class", str(relationship_id), "class"), stacklevel=2
        )
        return []
    edge_id = urllib.parse.quote(str(object_by_predicates["externalId"]))
    # If there is properties on the relationship, we create a new intermediate node
    edge_type = self._namespace[f"{source_type}To{target_type}Edge"]
    return self._create_edge(
        object_by_predicates, edge_id, source_id, target_id, self._predicate(target_type), edge_type
    )

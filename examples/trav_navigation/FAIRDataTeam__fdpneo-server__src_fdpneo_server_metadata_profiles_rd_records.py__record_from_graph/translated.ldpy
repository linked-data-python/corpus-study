# Extracted from FAIRDataTeam/fdpneo-server@3e72e119ae : src/fdpneo_server/metadata/profiles/rd_records.py
# region: record_from_graph (lines 141-178, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, URIRef
from fdpneo_server.shared.namespaces import (
    FDP_CHILD_LINK,
    FDP_CHILD_TAGS_URI,
    FDP_CHILD_TARGET,
    FDP_CHILD_TITLE,
    FDP_NAME,
    FDP_RELATION_URI,
    FDP_RESOURCE_DEFINITION,
    FDP_URL_PREFIX,
    LDP,
    bind_all,
)

def record_from_graph(graph: Graph, iri: str) -> ResourceDefinitionRecord:
    """Parse the RD record rooted at ``iri`` out of ``graph``.

    Raises :class:`ResourceDefinitionParseError` if a required term
    (``fdp:urlPrefix``, ``fdp:name``, ``ldp:constrainedBy``) is absent.
    """
    subject = URIRef(iri)
    url_prefix = _one_literal(graph, subject, FDP_URL_PREFIX, iri, "fdp:urlPrefix")
    name = _one_literal(graph, subject, FDP_NAME, iri, "fdp:name")
    schema_iri = _one_iri(graph, subject, LDP.constrainedBy, iri, "ldp:constrainedBy")

    children: list[ChildLinkRecord] = []
    for node in graph.objects(subject, FDP_CHILD_LINK):
        if not isinstance(node, (URIRef, BNode)):
            # A literal hung off fdp:childLink is malformed; the predefined
            # shape rejects it on write, so ignore it rather than crash here.
            continue
        relation = _one_iri(graph, node, FDP_RELATION_URI, iri, "fdp:relationUri")
        target = _one_literal(graph, node, FDP_CHILD_TARGET, iri, "fdp:childTarget")
        title_obj = graph.value(node, FDP_CHILD_TITLE)
        tags_obj = graph.value(node, FDP_CHILD_TAGS_URI)
        children.append(
            ChildLinkRecord(
                relation_uri=relation,
                target_prefix=target,
                title=str(title_obj) if title_obj is not None else "",
                tags_uri=str(tags_obj) if tags_obj is not None else None,
            )
        )
    # Sort children deterministically — RDF stores blank nodes unordered, and
    # callers (cache builder, OpenAPI generator) benefit from a stable order.
    children.sort(key=lambda c: (c.relation_uri, c.target_prefix))
    return ResourceDefinitionRecord(
        url_prefix=url_prefix,
        name=name,
        schema_iri=schema_iri,
        children=tuple(children),
    )

# Extracted from FAIRDataTeam/fdpneo-server@3e72e119ae : src/fdpneo_server/metadata/ldp/router.py
# region: _minimize_container (lines 724-742, stratum ns_import_project)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef
from fdpneo_server.metadata.graphs import (
    is_meta_graph_uri,
    record_graph_uri,
    record_uri_from_sibling,
)
from fdpneo_server.shared.namespaces import DCT, LDP as LDP_NS

def _minimize_container(
    graph: Graph, container_iri: str, omit_containment: bool, omit_membership: bool
) -> None:
    """Drop containment and/or membership triples from a container representation.

    Containment is ``ldp:contains``; membership is each member link reached via the
    container's ``ldp:hasMemberRelation`` predicates (e.g. ``dcat:dataset``). The
    Direct-Container *configuration* triples (``ldp:membershipResource`` etc.) are
    kept — they describe the minimal container, they are not membership triples.
    """
    # Normalize to the canonical record IRI: the request URL for the root arrives
    # as ".../" but the stored container subject is slash-stripped, so a bare
    # URIRef(container_iri) would target the wrong subject and remove nothing.
    subject = record_graph_uri(container_iri)
    if omit_containment:
        graph.remove((subject, LDP_NS.contains, None))
    if omit_membership:
        for relation in set(graph.objects(subject, LDP_NS.hasMemberRelation)):
            graph.remove((subject, relation, None))

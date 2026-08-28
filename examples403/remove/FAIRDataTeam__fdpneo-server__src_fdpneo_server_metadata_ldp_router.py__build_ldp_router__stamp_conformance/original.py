# Extracted from FAIRDataTeam/fdpneo-server@3e72e119ae : src/fdpneo_server/metadata/ldp/router.py
# region: build_ldp_router._stamp_conformance (lines 280-302, stratum remove)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef
from fdpneo_server.metadata.prof import ensure_conformance
from fdpneo_server.shared.graphs import is_profile_graph_uri
from fdpneo_server.shared.namespaces import DCT, LDP as LDP_NS

async def _stamp_conformance(graph: Graph, iri: str, shape_iri: str | None) -> str | None:
    """Make the record self-describing (ADR-0019): stamp server-owned
    ``dct:conformsTo`` → the type's stable profile, return the profile *version*
    IRI to record as ``fdp-o:validatedAgainst`` in the meta graph.

    The profile (and the schema version snapshot it wraps) is provisioned on
    demand from the record's schema. Any client-supplied ``conformsTo`` into
    the managed profile namespace is dropped first — the validation binding is
    server-owned and must equal the type default (ADR-0019 §2); a client's
    ``conformsTo`` to some *other* vocabulary/profile is left untouched.
    """
    if triplestore is None or shape_iri is None:
        return None
    resolved = await ensure_conformance(triplestore, repo, schema_iri=shape_iri)
    if resolved is None:
        return None
    stable_profile, validated_against = resolved
    subject = URIRef(iri)
    for obj in list(graph.objects(subject, DCT.conformsTo)):
        if isinstance(obj, URIRef) and is_profile_graph_uri(obj):
            graph.remove((subject, DCT.conformsTo, obj))
    graph.add((subject, DCT.conformsTo, URIRef(stable_profile)))
    return validated_against

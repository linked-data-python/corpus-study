# Extracted from FAIRDataTeam/fdpneo-server@3e72e119ae : src/fdpneo_server/metadata/profiles/applier.py
# region: _repository_graph (lines 451-486, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import RDF
from context_shim import DCAT, DCT, LDP, ODRL, VOID, direct_container_config, _service_advertisement

def _repository_graph(
    *,
    iri: str,
    type_iri: str,
    member_relations: list[str],
    title: str,
    rights_iri: str | None,
    search_enabled: bool = True,
) -> Graph:
    """Build the seed graph for the root record (the FAIR Data Point).

    The root is the single mandatory FDP resource (architecture §10). Sat at the
    API root, typed as the root RD's schema *class* (``type_iri`` — so the
    shape's ``sh:targetClass`` matches) and as a genuine LDP **Direct Container**
    (ADR-0008, task 15.1): it carries the membership configuration
    (``ldp:membershipResource`` = itself, one ``ldp:hasMemberRelation`` per RD
    child relation, ``ldp:insertedContentRelation ldp:MemberSubject``) so a
    standards consumer reads the container's membership pattern directly.

    It also **advertises this FDP's query service endpoints** (ADR-0018 gap G-05):
    ``void:sparqlEndpoint`` for the SPARQL endpoint plus a ``dcat:DataService``
    (``dcat:service`` → ``dcat:endpointURL``) for SPARQL and, when enabled, the
    search API — so an agent/client (e.g. the ``fdp-mcp`` bridge) discovers them
    from the root record instead of being hand-configured with endpoint paths.
    """
    subject = URIRef(iri)
    graph = Graph()
    graph.add((subject, RDF.type, URIRef(type_iri)))
    graph.add((subject, DCT.title, Literal(title)))
    if rights_iri is not None:
        graph.add((subject, DCT.rights, URIRef(rights_iri)))
    for triple in direct_container_config(subject, member_relations):
        graph.add(triple)
    for triple in _service_advertisement(subject, iri, search_enabled=search_enabled):
        graph.add(triple)
    return graph

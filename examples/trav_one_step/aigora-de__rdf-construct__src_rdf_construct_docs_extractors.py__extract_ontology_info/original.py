# Extracted from aigora-de/rdf-construct@670e400ea4 : src/rdf_construct/docs/extractors.py
# region: extract_ontology_info (lines 526-600, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import BNode, RDF, RDFS, Literal, URIRef
from rdflib.namespace import DCTERMS, OWL, SH, SKOS

def extract_ontology_info(graph: Graph) -> OntologyInfo:
    """Extract metadata about the ontology itself.

    Args:
        graph: RDF graph to extract ontology info from.

    Returns:
        OntologyInfo with ontology-level metadata.
    """
    info = OntologyInfo()

    # Find ontology URI
    for s in graph.subjects(RDF.type, OWL.Ontology):
        if isinstance(s, URIRef):
            info.uri = s
            break

    if info.uri:
        # Title
        info.title = get_label(graph, info.uri)
        if not info.title:
            # Try dcterms:title
            for obj in graph.objects(info.uri, DCTERMS.title):
                if isinstance(obj, Literal):
                    info.title = str(obj)
                    break

        # Description
        info.description = get_definition(graph, info.uri)

        # Version
        for obj in graph.objects(info.uri, OWL.versionInfo):
            if isinstance(obj, Literal):
                info.version = str(obj)
                break

        # Creators
        for obj in graph.objects(info.uri, DCTERMS.creator):
            if isinstance(obj, Literal):
                info.creators.append(str(obj))
            elif isinstance(obj, URIRef):
                info.creators.append(str(obj))

        # Contributors
        for obj in graph.objects(info.uri, DCTERMS.contributor):
            if isinstance(obj, Literal):
                info.contributors.append(str(obj))
            elif isinstance(obj, URIRef):
                info.contributors.append(str(obj))

        # Imports
        for obj in graph.objects(info.uri, OWL.imports):
            if isinstance(obj, URIRef):
                info.imports.append(obj)

        # Annotations
        info.annotations = get_annotations(graph, info.uri)

    # Namespaces - only include those actually used in triples
    used_uris: set[str] = set()
    for s, p, o in graph:
        if isinstance(s, URIRef):
            used_uris.add(str(s))
        if isinstance(p, URIRef):
            used_uris.add(str(p))
        if isinstance(o, URIRef):
            used_uris.add(str(o))

    # Only include namespaces that match at least one used URI
    for prefix, namespace in graph.namespaces():
        ns_str = str(namespace)
        if any(uri.startswith(ns_str) for uri in used_uris):
            info.namespaces[prefix] = ns_str

    return info

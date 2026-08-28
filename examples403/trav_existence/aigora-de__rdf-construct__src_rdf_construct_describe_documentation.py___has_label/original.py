# Extracted from aigora-de/rdf-construct@670e400ea4 : src/rdf_construct/describe/documentation.py
# region: _has_label (lines 115-128, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, RDF, RDFS
LABEL_PREDICATES = {
    RDFS.label,
    URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"),
    URIRef("http://www.w3.org/2004/02/skos/core#altLabel"),
    URIRef("http://purl.org/dc/elements/1.1/title"),
    URIRef("http://purl.org/dc/terms/title"),
}

def _has_label(graph: Graph, subject: URIRef) -> bool:
    """Check if a subject has any label predicate.

    Args:
        graph: RDF graph to query.
        subject: Subject to check.

    Returns:
        True if subject has at least one label.
    """
    for pred in LABEL_PREDICATES:
        if any(graph.objects(subject, pred)):
            return True
    return False

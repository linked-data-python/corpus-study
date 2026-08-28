# Extracted from aigora-de/rdf-construct@670e400ea4 : src/rdf_construct/stats/metrics/documentation.py
# region: _has_any_predicate (lines 71-85, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib import Graph, RDF, RDFS, Namespace

def _has_any_predicate(graph: Graph, subject: object, predicates: tuple) -> bool:
    """Check if subject has any of the given predicates.

    Args:
        graph: RDF graph to query.
        subject: Subject to check.
        predicates: Tuple of predicates to look for.

    Returns:
        True if subject has at least one of the predicates.
    """
    for pred in predicates:
        if graph.value(subject, pred) is not None:
            return True
    return False

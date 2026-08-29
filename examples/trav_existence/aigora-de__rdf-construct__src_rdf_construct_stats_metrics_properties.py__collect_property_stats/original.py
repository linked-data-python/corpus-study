# Extracted from aigora-de/rdf-construct@670e400ea4 : src/rdf_construct/stats/metrics/properties.py
# region: collect_property_stats (lines 48-88, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib import Graph, RDF, RDFS
from rdflib.namespace import OWL

def collect_property_stats(graph: Graph) -> PropertyStats:
    """Collect property statistics from an RDF graph.

    Args:
        graph: RDF graph to analyse.

    Returns:
        PropertyStats with all property metrics populated.
    """
    properties = _get_all_properties(graph)
    total = len(properties)

    if total == 0:
        return PropertyStats()

    # Count properties with domain
    with_domain = sum(1 for p in properties if graph.value(p, RDFS.domain) is not None)

    # Count properties with range
    with_range = sum(1 for p in properties if graph.value(p, RDFS.range) is not None)

    # Count inverse pairs (each owl:inverseOf creates a pair)
    # Count unique pairs (A inverseOf B = B inverseOf A)
    inverse_subjects = set(graph.subjects(OWL.inverseOf, None))
    inverse_pairs = len(inverse_subjects)  # Each subject represents one pair relationship

    # Count functional properties
    functional = len(set(graph.subjects(RDF.type, OWL.FunctionalProperty)))

    # Count symmetric properties
    symmetric = len(set(graph.subjects(RDF.type, OWL.SymmetricProperty)))

    return PropertyStats(
        with_domain=with_domain,
        with_range=with_range,
        domain_coverage=round(with_domain / total, 3) if total else 0.0,
        range_coverage=round(with_range / total, 3) if total else 0.0,
        inverse_pairs=inverse_pairs,
        functional=functional,
        symmetric=symmetric,
    )

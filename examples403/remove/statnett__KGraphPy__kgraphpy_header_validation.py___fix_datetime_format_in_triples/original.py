# Extracted from statnett/KGraphPy@38859be62f : kgraphpy/header_validation.py
# region: _fix_datetime_format_in_triples (lines 112-138, stratum remove)
# licence of the source repository: see meta.json
from rdflib import XSD, BNode, Literal, Node, Graph, URIRef
from rdflib.namespace import DCAT, DCTERMS, RDF
logger = logging.getLogger("cimxml_logger")

def _fix_datetime_format_in_triples(graph: Graph) -> None:
    """Fix datetime format for triples with these predicates:

        - dcat:endDate
        - dcat:startDate
        - dcterms:issued

    Parameters:
        graph (Graph): The graph to fix.
    """
    predicates = {DCAT.endDate, DCAT.startDate, DCTERMS.issued}
    triples = {
    (s, p, o)
    for s, p, o in graph.triples((None, None, None))
    if p in predicates
    }

    for s, p, o in triples:
        new_obj = _fix_datetime_format(o)
        if new_obj is None:
            logger.error(f"Found None for {p}. Expected a datetime.")
            continue

        if new_obj != o:
            graph.remove((s, p, o))
            graph.add((s, p, new_obj))
            logger.error(f"Corrected date format for predicate {p}: from {o} to {new_obj}.")

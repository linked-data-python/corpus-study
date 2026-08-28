# Extracted from statnett/KGraphPy@38859be62f : kgraphpy/header_validation.py
# region: _fix_cimxml_period_of_time_format (lines 268-286, stratum remove)
# licence of the source repository: see meta.json
from rdflib import XSD, BNode, Literal, Node, Graph, URIRef
from rdflib.namespace import DCAT, DCTERMS, RDF
logger = logging.getLogger("cimxml_logger")

def _fix_cimxml_period_of_time_format(graph: Graph, identifier: URIRef) -> None:
    """Fix the format of dcterms:PeriodOfTime representation in CIMXML header, including dcat:startDate and dcat:endDate triples.

    dcterms:temporal and rdf:type dcterms:PeriodOfTime triples are removed if any are present.

    Parameters:
        graph (Graph): The graph to fix.
        identifier (URIRef): The identifier to use for the dummy triple of startDate and endDate if missing.
    """
    for s, p, o in list(graph.triples((None, DCTERMS.temporal, None))):
        graph.remove((s, p, o))

    for s in graph.subjects(RDF.type, DCTERMS.PeriodOfTime):
        graph.remove((s, RDF.type, DCTERMS.PeriodOfTime))

    for predicate in [DCAT.startDate, DCAT.endDate]:
        triples = list(graph.triples((None, predicate, None)))
        if len(triples) > 1:
            logger.error(f"Multiple {predicate} triples found. All but one should be removed.")

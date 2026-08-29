# Extracted from statnett/KGraphPy@38859be62f : kgraphpy/header_validation.py
# region: has_complete_temporal (lines 180-192, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib import XSD, BNode, Literal, Node, Graph, URIRef
from rdflib.namespace import DCAT, DCTERMS, RDF

def has_complete_temporal(graph: Graph, identifier: URIRef) -> bool:
    # Find the blank node connected via dcterms:temporal
    for o in graph.objects(identifier, DCTERMS.temporal):
        if isinstance(o, BNode):
            # Check required triples
            type_ok = (o, RDF.type, DCTERMS.PeriodOfTime) in graph
            start_ok = any(graph.objects(o, DCAT.startDate))
            end_ok = any(graph.objects(o, DCAT.endDate))

            if type_ok and start_ok and end_ok:
                return True

    return False

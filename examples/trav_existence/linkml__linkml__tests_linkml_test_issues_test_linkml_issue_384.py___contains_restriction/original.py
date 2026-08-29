# Extracted from linkml/linkml@680595df54 : tests/linkml/test_issues/test_linkml_issue_384.py
# region: _contains_restriction (lines 56-61, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef
from rdflib.namespace import OWL, RDF, RDFS, XSD

def _contains_restriction(g: Graph, c: URIRef, prop: URIRef, pred: URIRef, filler: URIRef) -> bool:
    for r in g.objects(c, RDFS.subClassOf):
        if prop in g.objects(r, OWL.onProperty):
            if filler in g.objects(r, pred):
                return True
    return False

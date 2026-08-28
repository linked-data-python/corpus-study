# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: Class._set_subClassOf (lines 1077-1082, band medium)
# licence of the source repository: see meta.json
from rdflib import (
    BNode,
    Literal,
    Namespace,
    RDF,
    RDFS,
    URIRef,
    Variable
)

def _set_subClassOf(self, other):
    if not other:
        return
    for sc in other:
        self.graph.add(
            (self.identifier, RDFS.subClassOf, classOrIdentifier(sc)))

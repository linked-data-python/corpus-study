# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: Property._set_subPropertyOf (lines 2048-2053, band medium)
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

def _set_subPropertyOf(self, other):
    if not other:
        return
    for sP in other:
        self.graph.add(
            (self.identifier, RDFS.subPropertyOf, classOrIdentifier(sP)))

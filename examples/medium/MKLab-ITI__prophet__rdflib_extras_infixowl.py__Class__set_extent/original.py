# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: Class._set_extent (lines 977-981, band medium)
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

def _set_extent(self, other):
    if not other:
        return
    for m in other:
        self.graph.add((classOrIdentifier(m), RDF.type, self.identifier))

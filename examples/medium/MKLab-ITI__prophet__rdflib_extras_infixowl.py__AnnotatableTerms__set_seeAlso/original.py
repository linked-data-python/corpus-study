# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: AnnotatableTerms._set_seeAlso (lines 587-591, band medium)
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

def _set_seeAlso(self, seeAlsos):
    if not seeAlsos:
        return
    for s in seeAlsos:
        self.graph.add((self.identifier, RDFS.seeAlso, s))

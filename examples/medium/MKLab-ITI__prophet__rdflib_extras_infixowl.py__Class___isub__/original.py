# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: Class.__isub__ (lines 1021-1025, band medium)
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

def __isub__(self, other):
    assert isinstance(other, Class)
    self.graph.remove(
        (classOrIdentifier(other), RDFS.subClassOf, self.identifier))
    return self

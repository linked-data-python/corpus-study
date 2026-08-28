# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: Property._set_domain (lines 2084-2093, band medium)
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
from rdflib.term import Identifier

def _set_domain(self, other):
    if not other:
        return
    if isinstance(other, (Individual, Identifier)):
        self.graph.add(
            (self.identifier, RDFS.domain, classOrIdentifier(other)))
    else:
        for dom in other:
            self.graph.add(
                (self.identifier, RDFS.domain, classOrIdentifier(dom)))

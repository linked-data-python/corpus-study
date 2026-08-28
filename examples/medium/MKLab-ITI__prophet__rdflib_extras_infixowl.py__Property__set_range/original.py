# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: Property._set_range (lines 2106-2115, band medium)
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

def _set_range(self, ranges):
    if not ranges:
        return
    if isinstance(ranges, (Individual, Identifier)):
        self.graph.add(
            (self.identifier, RDFS.range, classOrIdentifier(ranges)))
    else:
        for range in ranges:
            self.graph.add(
                (self.identifier, RDFS.range, classOrIdentifier(range)))

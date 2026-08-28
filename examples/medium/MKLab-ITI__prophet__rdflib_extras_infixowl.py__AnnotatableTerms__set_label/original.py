# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: AnnotatableTerms._set_label (lines 603-610, band medium)
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

def _set_label(self, label):
    if not label:
        return
    if isinstance(label, Identifier):
        self.graph.add((self.identifier, RDFS.label, label))
    else:
        for l in label:
            self.graph.add((self.identifier, RDFS.label, l))

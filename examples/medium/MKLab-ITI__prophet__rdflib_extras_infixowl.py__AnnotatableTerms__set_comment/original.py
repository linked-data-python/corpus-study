# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: AnnotatableTerms._set_comment (lines 567-574, band medium)
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

def _set_comment(self, comment):
    if not comment:
        return
    if isinstance(comment, Identifier):
        self.graph.add((self.identifier, RDFS.comment, comment))
    else:
        for c in comment:
            self.graph.add((self.identifier, RDFS.comment, c))

# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: Class._set_equivalentClass (lines 1095-1100, band medium)
# licence of the source repository: see meta.json
from rdflib import Namespace
from infixowl_context import classOrIdentifier

OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

def _set_equivalentClass(self, other):
    if not other:
        return
    for sc in other:
        self.graph.add((self.identifier,
                       OWL_NS.equivalentClass, classOrIdentifier(sc)))

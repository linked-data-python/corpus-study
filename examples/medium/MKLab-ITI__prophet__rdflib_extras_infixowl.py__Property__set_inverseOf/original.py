# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: Property._set_inverseOf (lines 2067-2071, band medium)
# licence of the source repository: see meta.json
from rdflib import Namespace
from infixowl_shim import classOrIdentifier

OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

def _set_inverseOf(self, other):
    if not other:
        return
    self.graph.add(
        (self.identifier, OWL_NS.inverseOf, classOrIdentifier(other)))

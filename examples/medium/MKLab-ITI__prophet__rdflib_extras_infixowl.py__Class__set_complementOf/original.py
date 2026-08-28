# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: Class._set_complementOf (lines 1138-1142, band medium)
# licence of the source repository: see meta.json
from rdflib import Namespace
from infixowl_shim import classOrIdentifier  # context shim, see meta.json

OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

def _set_complementOf(self, other):
    if not other:
        return
    self.graph.add(
        (self.identifier, OWL_NS.complementOf, classOrIdentifier(other)))

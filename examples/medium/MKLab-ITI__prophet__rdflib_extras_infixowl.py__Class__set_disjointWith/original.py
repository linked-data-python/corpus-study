# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: Class._set_disjointWith (lines 1114-1119, band medium)
# licence of the source repository: see meta.json
from infixowl_context import Namespace, classOrIdentifier
OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

def _set_disjointWith(self, other):
    if not other:
        return
    for c in other:
        self.graph.add(
            (self.identifier, OWL_NS.disjointWith, classOrIdentifier(c)))

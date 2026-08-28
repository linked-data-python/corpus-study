# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: Individual._set_sameAs (lines 487-497, band medium)
# licence of the source repository: see meta.json
from rdflib import Namespace
from rdflib.term import Identifier
from infixowl_shim import Individual, classOrIdentifier
OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

def _set_sameAs(self, term):
    # if not kind:
    #     return
    if isinstance(term, (Individual, Identifier)):
        self.graph.add(
            (self.identifier, OWL_NS.sameAs, classOrIdentifier(term)))
    else:
        for c in term:
            assert isinstance(c, (Individual, Identifier))
            self.graph.add(
                (self.identifier, OWL_NS.sameAs, classOrIdentifier(c)))

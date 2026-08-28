# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: Class._get_extentQuery (lines 995-996, band medium)
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

def _get_extentQuery(self):
    return (Variable('CLASS'), RDF.type, self.identifier)

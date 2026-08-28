# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: Class.isPrimitive (lines 1204-1219, band medium)
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
# context shim (see meta.json): manchesterSyntax is a module-level helper of
# the enclosing infixowl.py, vendored as infixowl_context.py
from infixowl_context import manchesterSyntax
OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

def isPrimitive(self):
    if (self.identifier, RDF.type, OWL_NS.Restriction) in self.graph:
        return False
    # sc = list(self.subClassOf)
    ec = list(self.equivalentClass)
    for boolClass, p, rdfList in self.graph.triples_choices(
        (self.identifier,
         [OWL_NS.intersectionOf,
          OWL_NS.unionOf],
         None)):
        ec.append(manchesterSyntax(rdfList, self.graph, boolean=p))
    for e in ec:
        return False
    if self.complementOf:
        return False
    return True

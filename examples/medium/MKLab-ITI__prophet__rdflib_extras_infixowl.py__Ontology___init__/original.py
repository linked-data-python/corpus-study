# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: Ontology.__init__ (lines 631-637, band medium)
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
OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

def __init__(self,
             identifier=None, imports=None, comment=None, graph=None):
    super(Ontology, self).__init__(identifier, graph)
    self.imports = imports and imports or []
    self.comment = comment and comment or []
    if (self.identifier, RDF.type, OWL_NS.Ontology) not in self.graph:
        self.graph.add((self.identifier, RDF.type, OWL_NS.Ontology))

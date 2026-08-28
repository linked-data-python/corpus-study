# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/plugins/sparql/sparql.py
# region: Prologue.__init__ (lines 347-350, band low)
# licence of the source repository: see meta.json
from rdflib.namespace import NamespaceManager
from rdflib import Variable, BNode, Graph, ConjunctiveGraph, URIRef, Literal

def __init__(self):
    self.base = None
    self.namespace_manager = NamespaceManager(
        Graph())  # ns man needs a store

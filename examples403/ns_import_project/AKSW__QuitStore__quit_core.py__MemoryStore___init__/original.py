# Extracted from AKSW/QuitStore@7567c25da5 : quit/core.py
# region: MemoryStore.__init__ (lines 65-72, stratum ns_import_project)
# licence of the source repository: see meta.json
from rdflib import Graph, ConjunctiveGraph, BNode, Literal, URIRef
from quit.namespace import RDFS, FOAF, XSD, PROV, QUIT, is_a

def __init__(self, additional_bindings=list()):
    store = ConjunctiveGraph(identifier='default')
    nsBindings = [('quit', QUIT), ('foaf', FOAF), ('prov', PROV)]

    for prefix, namespace in nsBindings + additional_bindings:
        store.bind(prefix, namespace)

    super().__init__(store=store)

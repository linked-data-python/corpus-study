# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: GetIdentifiedClasses (lines 359-362, band medium)
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

def GetIdentifiedClasses(graph):
    for c in graph.subjects(predicate=RDF.type, object=OWL_NS.Class):
        if isinstance(c, URIRef):
            yield Class(c)

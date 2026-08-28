# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: AllClasses (lines 660-665, band medium)
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
from infixowl_shim import Class
OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

def AllClasses(graph):
    prevClasses = set()
    for c in graph.subjects(predicate=RDF.type, object=OWL_NS.Class):
        if c not in prevClasses:
            prevClasses.add(c)
            yield Class(c)

# --- demo harness, added identically to both representations (see meta.json).
# AllClasses is a generator, which the harness cannot compare directly, so the
# demo consumes it into observable module-level state.
from rdflib import Graph

demo_graph = Graph()
demo_graph.parse(data="""
    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix ex:  <http://example.org/> .
    ex:A a owl:Class .
    ex:B a owl:Class , owl:Thing .
    ex:B a owl:Class .
    ex:C a owl:Thing .
""", format="turtle")
demo_classes = list(AllClasses(demo_graph))
print(sorted(str(c.identifier) for c in demo_classes))

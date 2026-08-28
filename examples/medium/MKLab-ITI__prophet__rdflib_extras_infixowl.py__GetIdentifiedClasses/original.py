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
from infixowl_ctx import Class, Individual  # context shim, see infixowl_ctx.py
OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

def GetIdentifiedClasses(graph):
    for c in graph.subjects(predicate=RDF.type, object=OWL_NS.Class):
        if isinstance(c, URIRef):
            yield Class(c)

# --- demo harness: identical in original.py and translated.ldpy ---
# GetIdentifiedClasses is a generator, so the pair is compared through the
# module state it produces (demo_graph + stdout) rather than a return value.
from rdflib import Graph

Individual.factoryGraph = Graph()
demo_graph = Graph()
demo_graph.parse(data="""
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix ex:  <http://example.com/> .
ex:Brother a owl:Class .
ex:Sister a owl:Class .
[] a owl:Class .
ex:notAClass a owl:Thing .
""", format="turtle")
print(sorted(str(c.identifier) for c in GetIdentifiedClasses(demo_graph)))

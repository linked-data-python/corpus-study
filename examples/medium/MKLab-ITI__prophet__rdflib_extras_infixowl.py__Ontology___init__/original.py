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
from infixowl_ctx import Individual, Ontology  # context shim, see infixowl_ctx.py
OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

def __init__(self,
             identifier=None, imports=None, comment=None, graph=None):
    super(Ontology, self).__init__(identifier, graph)
    self.imports = imports and imports or []
    self.comment = comment and comment or []
    if (self.identifier, RDF.type, OWL_NS.Ontology) not in self.graph:
        self.graph.add((self.identifier, RDF.type, OWL_NS.Ontology))

# --- demo harness: identical in original.py and translated.ldpy ---
# The region is a constructor: it is run on a bare Ontology instance and the
# graph it fills is what the two sides are compared on.
from rdflib import Graph

Individual.factoryGraph = Graph()
demo_graph = Graph()
onto = Ontology.__new__(Ontology)
__init__(onto,
         URIRef("http://example.com/onto"),
         imports=[URIRef("http://example.com/other")],
         comment=[Literal("an ontology")],
         graph=demo_graph)
# second call: the rdf:type triple is already there, exercising the guard
__init__(onto, URIRef("http://example.com/onto"), graph=demo_graph)
print(len(demo_graph), sorted(str(p) for p in set(demo_graph.predicates())))

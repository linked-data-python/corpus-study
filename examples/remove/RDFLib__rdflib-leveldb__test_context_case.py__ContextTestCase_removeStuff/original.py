# Extracted from RDFLib/rdflib-leveldb@a0f3386c71 : test/context_case.py
# region: ContextTestCase.removeStuff (lines 56-65, stratum remove)
# licence of the source repository: see meta.json
from rdflib import Graph
michel = URIRef("urn:michel")
tarek = URIRef("urn:tarek")
bob = URIRef("urn:bob")
likes = URIRef("urn:likes")
hates = URIRef("urn:hates")
pizza = URIRef("urn:pizza")
cheese = URIRef("urn:cheese")
c1 = URIRef("urn:context-1")

def removeStuff(self):
    graph = Graph(self.graph.store, c1)

    graph.remove((tarek, likes, pizza))
    graph.remove((tarek, likes, cheese))
    graph.remove((michel, likes, pizza))
    graph.remove((michel, likes, cheese))
    graph.remove((bob, likes, cheese))
    graph.remove((bob, hates, pizza))
    graph.remove((bob, hates, michel))  # gasp!

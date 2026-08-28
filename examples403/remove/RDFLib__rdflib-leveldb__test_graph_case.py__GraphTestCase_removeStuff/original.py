# Extracted from RDFLib/rdflib-leveldb@a0f3386c71 : test/graph_case.py
# region: GraphTestCase.removeStuff (lines 40-47, stratum remove)
# licence of the source repository: see meta.json
michel = URIRef("urn:michel")
tarek = URIRef("urn:tarek")
bob = URIRef("urn:bob")
likes = URIRef("urn:likes")
hates = URIRef("urn:hates")
pizza = URIRef("urn:pizza")
cheese = URIRef("urn:cheese")

def removeStuff(self):
    self.graph.remove((tarek, likes, pizza))
    self.graph.remove((tarek, likes, cheese))
    self.graph.remove((michel, likes, pizza))
    self.graph.remove((michel, likes, cheese))
    self.graph.remove((bob, likes, cheese))
    self.graph.remove((bob, hates, pizza))
    self.graph.remove((bob, hates, michel))  # gasp!

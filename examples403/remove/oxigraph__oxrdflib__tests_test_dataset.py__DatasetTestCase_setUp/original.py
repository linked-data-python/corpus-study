# Extracted from oxigraph/oxrdflib@70b1268a8e : tests/test_dataset.py
# region: DatasetTestCase.setUp (lines 45-64, stratum remove)
# licence of the source repository: see meta.json
from rdflib import Dataset, URIRef

def setUp(self) -> None:
    self.graph = Dataset(store="Oxigraph")
    self.michel = URIRef("urn:michel")
    self.tarek = URIRef("urn:tarek")
    self.bob = URIRef("urn:bob")
    self.likes = URIRef("urn:likes")
    self.hates = URIRef("urn:hates")
    self.pizza = URIRef("urn:pizza")
    self.cheese = URIRef("urn:cheese")

    # Use regular URIs because SPARQL endpoints like Fuseki alter short names
    self.c1 = URIRef("urn:context-1")
    self.c2 = URIRef("urn:context-2")

    # delete the graph for each test!
    self.graph.remove((None, None, None))
    for c in self.graph.contexts():
        c.remove((None, None, None))
        self.assertEqual(len(c), 0)
        self.graph.remove_graph(c)

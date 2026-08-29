# Extracted from RDFLib/rdflib-leveldb@a0f3386c71 : test/test_store_performance2.py
# region: StoreTestCase.testSimpleGraph (lines 83-119, stratum bind_initbindings)
# licence of the source repository: see meta.json
from time import time
log = logging.getLogger(__name__)
michel = URIRef("urn:michel")
tarek = URIRef("urn:tarek")
bob = URIRef("urn:bob")
likes = URIRef("urn:likes")
pizza = URIRef("urn:pizza")
cheese = URIRef("urn:cheese")
graphuri = URIRef("urn:graph")
othergraphuri = URIRef("urn:othergraph")

def testSimpleGraph(self):
    t0 = time()
    g = self.graph.get_context(graphuri)
    g.add((tarek, likes, pizza))
    g.add((bob, likes, pizza))
    g.add((bob, likes, cheese))

    g2 = self.graph.get_context(othergraphuri)
    g2.add((michel, likes, pizza))

    self.assertEqual(3, len(g), "graph contains 3 triples")
    self.assertEqual(1, len(g2), "other graph contains 1 triple")

    r = g.query("SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }")
    self.assertEqual(2, len(list(r)), "two people like pizza")

    r = g.triples((None, likes, pizza))
    self.assertEqual(2, len(list(r)), "two people like pizza")

    # Test initBindings
    r = g.query(
        "SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }",
        initBindings={"s": tarek},
    )
    self.assertEqual(1, len(list(r)), "i was asking only about tarek")

    r = g.triples((tarek, likes, pizza))
    self.assertEqual(1, len(list(r)), "i was asking only about tarek")

    r = g.triples((tarek, likes, cheese))
    self.assertEqual(0, len(list(r)), "tarek doesn't like cheese")

    g2.add((tarek, likes, pizza))
    g.remove((tarek, likes, pizza))
    r = g.query("SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }")
    t1 = time()
    log.debug(f"testSimpleGraph {self.store}: {t1 - t0:.5f}")

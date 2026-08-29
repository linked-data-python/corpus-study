# Extracted from RDFLib/rdflib-leveldb@a0f3386c71 : test/test_store_performance2.py
# region: StoreTestCase.testConjunctiveDefault (lines 122-169, stratum sparql_literal)
# licence of the source repository: see meta.json
from time import time
log = logging.getLogger(__name__)
tarek = URIRef("urn:tarek")
bob = URIRef("urn:bob")
likes = URIRef("urn:likes")
hates = URIRef("urn:hates")
pizza = URIRef("urn:pizza")
cheese = URIRef("urn:cheese")
graphuri = URIRef("urn:graph")
othergraphuri = URIRef("urn:othergraph")

def testConjunctiveDefault(self):
    t0 = time()
    g = self.graph.get_context(graphuri)
    g.add((tarek, likes, pizza))
    g2 = self.graph.get_context(othergraphuri)
    g2.add((bob, likes, pizza))
    g.add((tarek, hates, cheese))

    self.assertEqual(2, len(g), "graph contains 2 triples")

    # the following are actually bad tests as they depend on your endpoint,
    # as pointed out in the sparqlstore.py code:
    #
    # # For ConjunctiveGraphs, reading is done from the "default graph" Exactly
    # # what this means depends on your endpoint, because SPARQL does not offer a
    # # simple way to query the union of all graphs as it would be expected for a
    # # ConjuntiveGraph.
    # #
    # # Fuseki/TDB has a flag for specifying that the default graph
    # # is the union of all graphs (tdb:unionDefaultGraph in the Fuseki config).
    self.assertEqual(
        3,
        len(self.graph),
        "default union graph should contain three triples but contains:\n"
        "%s" % list(self.graph),
    )

    r = self.graph.query("SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }")
    self.assertEqual(2, len(list(r)), "two people like pizza")

    r = self.graph.query(
        "SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }",
        initBindings={"s": tarek},
    )
    self.assertEqual(1, len(list(r)), "i was asking only about tarek")

    r = self.graph.triples((tarek, likes, pizza))
    self.assertEqual(1, len(list(r)), "i was asking only about tarek")

    r = self.graph.triples((tarek, likes, cheese))
    self.assertEqual(0, len(list(r)), "tarek doesn't like cheese")

    g2.remove((bob, likes, pizza))

    r = self.graph.query("SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }")
    self.assertEqual(1, len(list(r)), "only tarek likes pizza")
    t1 = time()
    log.debug(f"testConjunctiveDefault {self.store}: {t1 - t0:.5f}")

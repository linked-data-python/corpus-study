# Extracted from RDFLib/rdflib-leveldb@a0f3386c71 : test/test_store_performance2.py
# region: StoreTestCase.testNamedGraphUpdateWithInitBindings (lines 362-375, stratum sparql_literal)
# licence of the source repository: see meta.json
from time import time
from leveldb_shim import logging, URIRef  # context shim, see meta.json
log = logging.getLogger(__name__)
michel = URIRef("urn:michel")
likes = URIRef("urn:likes")
pizza = URIRef("urn:pizza")
graphuri = URIRef("urn:graph")

def testNamedGraphUpdateWithInitBindings(self):
    t0 = time()
    g = self.graph.get_context(graphuri)
    g.update("INSERT { ?a ?b ?c } WHERE {}", initBindings={"a": michel, "b": likes, "c": pizza})
    self.assertEqual(set(g), {(michel, likes, pizza)}, "only michel likes pizza")
    log.debug(f"testNamedGraphUpdateWithInitBindings {self.store}: {time() - t0:.5f}")

# Extracted from RDFLib/rdflib-leveldb@a0f3386c71 : test/test_functionality.py
# region: testSimpleGraph (lines 68-102, stratum remove)
# licence of the source repository: see meta.json
from rdflib import URIRef
michel = URIRef("urn:michel")
tarek = URIRef("urn:tarek")
bob = URIRef("urn:bob")
likes = URIRef("urn:likes")
pizza = URIRef("urn:pizza")
cheese = URIRef("urn:cheese")
graphuri = URIRef("urn:graph")
othergraphuri = URIRef("urn:othergraph")

def testSimpleGraph(getgraph):
    g = getgraph.get_context(graphuri)
    g.add((tarek, likes, pizza))
    g.add((bob, likes, pizza))
    g.add((bob, likes, cheese))

    g2 = getgraph.get_context(othergraphuri)
    g2.add((michel, likes, pizza))

    assert len(g) == 3  # "graph contains 3 triples")
    assert len(g2) == 1  # "other graph contains 1 triple")

    r = g.query("SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }")
    assert len(r) == 2  # "two people like pizza")

    assert len(list(g.triples((None, likes, pizza)))) == 2  # "two people like pizza")

    # Test initBindings
    r = g.query("SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }", initBindings={"s": tarek})
    assert len(r) == 1  # "i was asking only about tarek")

    assert (tarek, likes, pizza) in g  # "i was asking only about tarek")
    assert (tarek, likes, cheese) not in g  # "tarek doesn't like cheese")

    g2.add((tarek, likes, pizza))
    g.remove((tarek, likes, pizza))
    g.query("SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }")

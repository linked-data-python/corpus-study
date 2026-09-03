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
    graph = getgraph
    g = graph.get_context(graphuri)
    g.add((tarek, likes, pizza))
    g.add((bob, likes, pizza))
    g.add((bob, likes, cheese))

    g2 = graph.get_context(othergraphuri)
    g2.add((michel, likes, pizza))

    assert len(g) == 3  # "graph contains 3 triples")
    assert len(g2) == 1  # "other graph contains 1 triple")

    r = g.query("SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }")
    assert len(list(r)) == 2  # "two people like pizza")

    r = g.triples((None, likes, pizza))
    assert len(list(r)) == 2  # "two people like pizza")

    # Test initBindings
    r = g.query(
        "SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }",
        initBindings={"s": tarek},
    )
    assert len(list(r)) == 1  # "i was asking only about tarek")

    r = g.triples((tarek, likes, pizza))
    assert len(list(r)) == 1  # "i was asking only about tarek")

    r = g.triples((tarek, likes, cheese))
    assert len(list(r)) == 0  # "tarek doesn't like cheese")

    g2.add((tarek, likes, pizza))
    g.remove((tarek, likes, pizza))
    r = g.query("SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }")

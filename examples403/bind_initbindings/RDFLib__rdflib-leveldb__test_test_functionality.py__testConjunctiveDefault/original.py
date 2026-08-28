# Extracted from RDFLib/rdflib-leveldb@a0f3386c71 : test/test_functionality.py
# region: testConjunctiveDefault (lines 105-147, stratum bind_initbindings)
# licence of the source repository: see meta.json
tarek = URIRef("urn:tarek")
bob = URIRef("urn:bob")
likes = URIRef("urn:likes")
hates = URIRef("urn:hates")
pizza = URIRef("urn:pizza")
cheese = URIRef("urn:cheese")
graphuri = URIRef("urn:graph")
othergraphuri = URIRef("urn:othergraph")

def testConjunctiveDefault(getgraph):
    graph = getgraph
    g = graph.get_context(graphuri)
    g.add((tarek, likes, pizza))
    g2 = graph.get_context(othergraphuri)
    g2.add((bob, likes, pizza))
    g.add((tarek, hates, cheese))

    assert len(g) == 2  # "graph contains 2 triples")

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
    assert (
        len(graph) == 3
    )  # "default union graph should contain three triples but contains:\n" "%s" % list(graph),

    r = graph.query("SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }")
    assert len(list(r)) == 2  # "two people like pizza")

    r = graph.query(
        "SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }",
        initBindings={"s": tarek},
    )
    assert len(list(r)) == 1  # "i was asking only about tarek")

    r = graph.triples((tarek, likes, pizza))
    assert len(list(r)) == 1  # "i was asking only about tarek")

    r = graph.triples((tarek, likes, cheese))
    assert len(list(r)) == 0  # "tarek doesn't like cheese")

    g2.remove((bob, likes, pizza))

    r = graph.query("SELECT * WHERE { ?s <urn:likes> <urn:pizza> . }")
    assert len(list(r)) == 1  # "only tarek likes pizza")

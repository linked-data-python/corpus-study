# Extracted from RDFLib/rdflib-leveldb@a0f3386c71 : test/test_graph.py
# region: test_create_db (lines 56-63, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
michel = URIRef("urn:michel")
cheese = URIRef("urn:cheese")
likes = URIRef("urn:likes")
pizza = URIRef("urn:pizza")

def test_create_db(getgraph):
    graph = getgraph
    graph.add((michel, likes, pizza))
    graph.add((michel, likes, cheese))
    graph.commit()
    assert (
        len(graph) == 5
    )  # f"There must be three triples in the graph after the first data chunk parse, not {len(graph)}"

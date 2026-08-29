# Extracted from RDFLib/rdflib-leveldb@a0f3386c71 : test/test_functionality.py
# region: testUpdateWithInitNs (lines 160-170, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib import BNode, Literal, RDF, RDFS, URIRef, Variable
michel = URIRef("urn:michel")
likes = URIRef("urn:likes")
pizza = URIRef("urn:pizza")
graphuri = URIRef("urn:graph")

def testUpdateWithInitNs(getgraph):
    graph = getgraph
    graph.update(
        "INSERT DATA { GRAPH ns:graph { ns:michel ns:likes ns:pizza . } }",
        initNs={"ns": URIRef("urn:")},
    )

    g = graph.get_context(graphuri)
    assert set(g.triples((None, None, None))) == set(
        [(michel, likes, pizza)]
    )  # "only michel likes pizza"

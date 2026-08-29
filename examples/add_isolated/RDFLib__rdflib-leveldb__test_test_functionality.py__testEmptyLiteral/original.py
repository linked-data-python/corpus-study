# Extracted from RDFLib/rdflib-leveldb@a0f3386c71 : test/test_functionality.py
# region: testEmptyLiteral (lines 318-332, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import BNode, Literal, RDF, RDFS, URIRef, Variable
graphuri = URIRef("urn:graph")

def testEmptyLiteral(getgraph):
    graph = getgraph
    # test for https://github.com/RDFLib/rdflib/issues/457
    # also see test_issue457.py which is sparql store independent!
    g = graph.get_context(graphuri)
    g.add(
        (
            URIRef("http://example.com/s"),
            URIRef("http://example.com/p"),
            Literal(""),
        )
    )

    o = tuple(g)[0][2]
    assert o == Literal(""), repr(o)

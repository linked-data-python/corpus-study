# Extracted from oxigraph/oxrdflib@70b1268a8e : tests/test_store.py
# region: StoreTestCase._fill_graph (lines 53-60, stratum remove)
# licence of the source repository: see meta.json
from rdflib import RDF, XSD, BNode, ConjunctiveGraph, Graph, Literal, Namespace
EX = Namespace("http://example.com/")

@staticmethod
def _fill_graph(g: Graph) -> None:
    g.add((EX.foo, RDF.type, EX.Entity))
    g.add((EX.foo, EX.prop, BNode("123")))
    g.add((EX.foo, EX.prop1, Literal("foo")))
    g.add((EX.foo, EX.prop1, Literal("foo", lang="en")))
    g.add((EX.foo, EX.prop1, Literal("1", datatype=XSD.integer)))
    g.remove((EX.foo, EX.prop, BNode("123")))

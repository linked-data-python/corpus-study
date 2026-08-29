# Extracted from oxigraph/oxrdflib@70b1268a8e : tests/test_sparql.py
# region: SparqlTestCase.test_ask_query (lines 13-33, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import RDF, ConjunctiveGraph, Dataset, Graph, Namespace
EX = Namespace("http://example.com/")

def test_ask_query(self) -> None:
    g = ConjunctiveGraph("Oxigraph")
    g.add((EX.foo, RDF.type, EX.Entity))
    g.bind("ex", EX)

    # basic
    result = g.query("ASK { ?s ?p ?o }")
    self.assertTrue(result)
    self.assertIsInstance(result.serialize(), bytes)

    # with not initialized prefix
    self.assertTrue(g.query("ASK { ex:foo rdf:type ex2:Entity }", initNs={"ex2": EX}))

    # with init entities
    self.assertFalse(g.query("ASK { ?s ?p ?o }", initBindings={"o": EX.NotExists}))

    # in specific graph
    g = ConjunctiveGraph("Oxigraph")
    g1 = Graph(store=g.store, identifier=EX.g1)
    g1.add((EX.foo, RDF.type, EX.Entity))
    self.assertTrue(g1.query("ASK { ?s ?p ?o }"))

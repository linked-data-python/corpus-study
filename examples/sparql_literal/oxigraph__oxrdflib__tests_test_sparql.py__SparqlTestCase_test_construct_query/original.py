# Extracted from oxigraph/oxrdflib@70b1268a8e : tests/test_sparql.py
# region: SparqlTestCase.test_construct_query (lines 84-91, stratum sparql_literal)
# licence of the source repository: see meta.json
from rdflib import RDF, ConjunctiveGraph, Dataset, Graph, Namespace
EX = Namespace("http://example.com/")

def test_construct_query(self) -> None:
    g = ConjunctiveGraph("Oxigraph")
    g.add((EX.foo, RDF.type, EX.Entity))
    result = g.query("CONSTRUCT WHERE { ?s ?p ?o }")
    self.assertEqual(
        result.serialize(format="ntriples").strip(),
        b"<http://example.com/foo> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://example.com/Entity> .",
    )

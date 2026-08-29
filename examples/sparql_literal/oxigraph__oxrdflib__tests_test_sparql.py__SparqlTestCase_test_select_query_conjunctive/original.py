# Extracted from oxigraph/oxrdflib@70b1268a8e : tests/test_sparql.py
# region: SparqlTestCase.test_select_query_conjunctive (lines 47-57, stratum sparql_literal)
# licence of the source repository: see meta.json
import json
from rdflib import RDF, ConjunctiveGraph, Dataset, Graph, Namespace
EX = Namespace("http://example.com/")

def test_select_query_conjunctive(self) -> None:
    g = ConjunctiveGraph("Oxigraph")
    g.add((EX.foo, RDF.type, EX.Entity))
    result = g.query("SELECT ?s WHERE { ?s ?p ?o }")
    self.assertEqual(
        json.loads(result.serialize(format="json").decode("utf-8")),
        {
            "results": {"bindings": [{"s": {"type": "uri", "value": "http://example.com/foo"}}]},
            "head": {"vars": ["s"]},
        },
    )

# Extracted from oxigraph/oxrdflib@70b1268a8e : tests/test_sparql.py
# region: SparqlTestCase.test_select_query_init_bindings (lines 93-102, stratum bind_initbindings)
# licence of the source repository: see meta.json
import json
from rdflib import RDF, ConjunctiveGraph, Dataset, Graph, Namespace
EX = Namespace("http://example.com/")

def test_select_query_init_bindings(self) -> None:
    g = Graph("Oxigraph")
    result = g.query("SELECT ?s WHERE {}", initBindings={"s": EX.foo})
    self.assertEqual(
        json.loads(result.serialize(format="json").decode("utf-8")),
        {
            "results": {"bindings": [{"s": {"type": "uri", "value": "http://example.com/foo"}}]},
            "head": {"vars": ["s"]},
        },
    )

# Extracted from oxigraph/oxrdflib@70b1268a8e : tests/test_sparql.py
# region: SparqlTestCase.test_insert_where_update_dataset_named_graph (lines 127-131, stratum sparql_literal)
# licence of the source repository: see meta.json
from rdflib import RDF, ConjunctiveGraph, Dataset, Graph, Namespace
EX = Namespace("http://example.com/")

def test_insert_where_update_dataset_named_graph(self) -> None:
    g = Dataset("Oxigraph")
    g.add((EX.foo, RDF.type, EX.Entity, EX.g))
    g.update("INSERT { ?s a <http://example.com/Entity2> } WHERE { GRAPH ?g { ?s a <http://example.com/Entity> } }")
    self.assertIn((EX.foo, RDF.type, EX.Entity2, g.identifier), g)

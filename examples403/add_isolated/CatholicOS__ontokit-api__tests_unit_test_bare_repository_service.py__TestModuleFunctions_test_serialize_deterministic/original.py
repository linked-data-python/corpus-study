# Extracted from CatholicOS/ontokit-api@23680a4d04 : tests/unit/test_bare_repository_service.py
# region: TestModuleFunctions.test_serialize_deterministic (lines 1072-1083, stratum add_isolated)
# licence of the source repository: see meta.json
def test_serialize_deterministic(self) -> None:
    """serialize_deterministic produces consistent Turtle output."""
    from rdflib import OWL, RDF, Graph, URIRef

    from ontokit.git.bare_repository import serialize_deterministic

    g = Graph()
    iri = URIRef("http://example.org/ontology")
    g.add((iri, RDF.type, OWL.Ontology))
    result = serialize_deterministic(g)
    assert isinstance(result, str)
    assert "Ontology" in result

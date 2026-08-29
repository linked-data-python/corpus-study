# Extracted from linkml/linkml@680595df54 : tests/linkml_runtime/test_loaders_dumpers/test_loaders_no_namespace.py
# region: test_schema_load_no_namespace (lines 35-73, stratum trav_existence)
# licence of the source repository: see meta.json
import pytest
import rdflib

@pytest.mark.parametrize(
    ("subject", "predicate", "object"),
    [
        (
            None,
            rdflib.term.URIRef("https://w3id.org/linkml/personinfo/source"),
            rdflib.term.URIRef("https://example.org/source"),
        ),
        (
            None,
            rdflib.term.URIRef("https://w3id.org/linkml/personinfo/pets"),
            rdflib.term.URIRef("https://example.org/PetA"),
        ),
        (
            rdflib.term.URIRef("http://example.org/default/org%201"),
            rdflib.term.URIRef("http://schema.org/name"),
            rdflib.term.Literal("Acme Inc. (US)"),
        ),
        (
            rdflib.term.URIRef("https://example.org/P1"),
            rdflib.term.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            rdflib.term.URIRef("http://schema.org/Person"),
        ),
        (
            rdflib.term.URIRef("https://example.org/P1"),
            rdflib.term.URIRef("http://schema.org/name"),
            rdflib.term.Literal("John Doe"),
        ),
    ],
)
def test_schema_load_no_namespace(graph: rdflib.Graph, subject, predicate, object) -> None:
    """Test loading schema and dataset with no namespace using rdflib.

    https://github.com/linkml/linkml/issues/576
    """
    if subject is None:
        assert object in graph.objects(subject, predicate)
    else:
        assert (subject, predicate, object) in graph

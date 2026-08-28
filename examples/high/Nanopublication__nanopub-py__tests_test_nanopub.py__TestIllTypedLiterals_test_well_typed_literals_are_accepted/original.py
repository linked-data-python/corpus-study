# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: TestIllTypedLiterals.test_well_typed_literals_are_accepted (lines 843-859, band high)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, URIRef, Dataset, DC, RDF, Namespace, DCTERMS, PROV, XSD

def test_well_typed_literals_are_accepted(self):
    np = _minimal_valid_nanopub()
    for i, literal in enumerate([
        Literal("42", datatype=XSD.integer),
        Literal(42),
        Literal("2020-01-01T00:00:00", datatype=XSD.dateTime),
        Literal("false", datatype=XSD.boolean),
        Literal("plain string"),
        Literal("a string", lang="en"),
        # Unrecognized datatypes cannot be checked, and must not be rejected
        Literal("whatever", datatype=URIRef("http://example.org/myDatatype")),
    ]):
        np.assertion.add(
            (URIRef("http://test"), URIRef(f"http://example.org/p{i}"), literal)
        )
    assert np.ill_typed_literals == []
    assert np.is_valid

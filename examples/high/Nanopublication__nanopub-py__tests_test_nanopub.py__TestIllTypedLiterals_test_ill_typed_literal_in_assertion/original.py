# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: TestIllTypedLiterals.test_ill_typed_literal_in_assertion (lines 783-794, band high)
# licence of the source repository: see meta.json
import pytest
from rdflib import BNode, Graph, Literal, URIRef, Dataset, DC, RDF, Namespace, DCTERMS, PROV, XSD
from nanopub.utils import MalformedNanopubError

def test_ill_typed_literal_in_assertion(self):
    np = _minimal_valid_nanopub()
    np.assertion.add(
        (
            URIRef("http://test"),
            URIRef("http://example.org/count"),
            Literal("not-a-number", datatype=XSD.integer),
        )
    )
    assert [str(o) for o, _ in np.ill_typed_literals] == ["not-a-number"]
    with pytest.raises(MalformedNanopubError, match="not-a-number"):
        np.is_valid

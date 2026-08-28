# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: TestIllTypedLiterals.test_sign_rejects_ill_typed_literal (lines 861-872, band high)
# licence of the source repository: see meta.json
import pytest
from rdflib import BNode, Graph, Literal, URIRef, Dataset, DC, RDF, Namespace, DCTERMS, PROV, XSD
from nanopub.utils import MalformedNanopubError
from tests.conftest import (
    default_conf,
    profile_test,
    skip_if_nanopub_server_unavailable, testsuite, testsuite_conf,
)

def test_sign_rejects_ill_typed_literal(self):
    np = _minimal_valid_nanopub(conf=default_conf)
    np.assertion.add(
        (
            URIRef("http://test"),
            URIRef("http://example.org/count"),
            Literal("not-a-number", datatype=XSD.integer),
        )
    )
    with pytest.raises(MalformedNanopubError, match="not-a-number"):
        np.sign()
    assert np.source_uri is None

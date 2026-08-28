# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: TestSign.test_sign_artifactcode_placeholder_in_custom_namespace (lines 532-555, band high)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, URIRef, Dataset, DC, RDF, Namespace, DCTERMS, PROV, XSD
from nanopub import (
    Nanopub,
    NanopubConf,
    namespaces,
)
from nanopub.definitions import NP_PREFIX
from tests.conftest import (
    default_conf,
    profile_test,
    skip_if_nanopub_server_unavailable, testsuite, testsuite_conf,
)

def test_sign_artifactcode_placeholder_in_custom_namespace(self, testsuite):
    """Signing a nanopub that mints a concept in a custom namespace via the
    ``~~~ARTIFACTCODE~~~`` placeholder gives that concept the same trusty
    code as the nanopub itself, and the result is valid (see issue #232)."""
    tc = next(
        tc for tc in testsuite.get_transform_cases("rsa-key1")
        if tc.plain.name == "artifactcode-1.in.trig"
    )
    ds = Dataset()
    ds.parse(data=tc.plain.read_text(), format="trig")
    np = Nanopub(conf=testsuite_conf, rdf=ds)
    np.sign()

    assert np.has_valid_signature
    assert np.has_valid_trusty
    assert np.is_valid

    # The concept minted in the custom namespace must carry the nanopub's
    # trusty code, and the placeholder must be gone everywhere.
    artifact_code = str(np.source_uri).removeprefix(NP_PREFIX)
    concept = URIRef(f"https://example.org/ns/{artifact_code}")
    terms = {term for quad in np.rdf.quads((None, None, None, None)) for term in quad}
    assert concept in terms
    assert all("~~~ARTIFACTCODE~~~" not in str(term) for term in terms)

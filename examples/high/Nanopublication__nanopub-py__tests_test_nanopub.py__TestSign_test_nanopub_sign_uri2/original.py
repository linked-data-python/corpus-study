# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: TestSign.test_nanopub_sign_uri2 (lines 516-530, band high)
# licence of the source repository: see meta.json
import nanopub_shim  # noqa: F401  context shim, see meta.json
from rdflib import BNode, Graph, Literal, URIRef, Dataset, DC, RDF, Namespace, DCTERMS, PROV, XSD
from nanopub import (
    Nanopub,
    NanopubConf,
    namespaces,
)
from conftest_shim import (
    default_conf,
    profile_test,
    skip_if_nanopub_server_unavailable, testsuite, testsuite_conf,
)

def test_nanopub_sign_uri2(self):
    expected_trusty = "RAIh8Oq-29dIVTZDhETpJ6f8oxxrILbZ3gSxkyAQY4220"
    np = Nanopub(
        conf=default_conf,
    )
    np.assertion.add(
        (
            URIRef("http://test"),
            namespaces.HYCL.claims,
            Literal("This is a test of nanopub-python"),
        )
    )
    np.sign()
    assert np.has_valid_signature
    assert expected_trusty in np.source_uri

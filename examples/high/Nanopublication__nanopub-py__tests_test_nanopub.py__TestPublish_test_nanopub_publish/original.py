# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: TestPublish.test_nanopub_publish (lines 668-681, band high)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, URIRef, Dataset, DC, RDF, Namespace, DCTERMS, PROV, XSD
from nanopub import (
    Nanopub,
    NanopubConf,
    namespaces,
)
from tests.conftest import (
    default_conf,
    profile_test,
    skip_if_nanopub_server_unavailable, testsuite, testsuite_conf,
)

def test_nanopub_publish(self):
    expected_trusty = "RAIh8Oq-29dIVTZDhETpJ6f8oxxrILbZ3gSxkyAQY4220"
    assertion = Graph()
    assertion.add(
        (
            URIRef("http://test"),
            namespaces.HYCL.claims,
            Literal("This is a test of nanopub-python"),
        )
    )
    np = Nanopub(conf=default_conf, assertion=assertion)
    np.publish()
    assert np.has_valid_signature
    assert expected_trusty in np.source_uri

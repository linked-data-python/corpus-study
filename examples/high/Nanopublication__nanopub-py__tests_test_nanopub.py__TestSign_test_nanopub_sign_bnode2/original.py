# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: TestSign.test_nanopub_sign_bnode2 (lines 572-592, band high)
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

def test_nanopub_sign_bnode2(self):
    expected_trusty = "RA-1eE8scfVaiK7vP4CZueTyEyRmn1g2PpPf-j69WQAgM"
    assertion = Graph()
    assertion.add(
        (
            BNode("test"),
            namespaces.HYCL.claims,
            Literal("This is a test of nanopub-python"),
        )
    )
    assertion.add(
        (
            BNode("test2"),
            namespaces.HYCL.claims,
            Literal("This is another test of nanopub-python"),
        )
    )
    np = Nanopub(conf=default_conf, assertion=assertion)
    np.sign()
    assert expected_trusty in np.source_uri
    assert np.has_valid_signature

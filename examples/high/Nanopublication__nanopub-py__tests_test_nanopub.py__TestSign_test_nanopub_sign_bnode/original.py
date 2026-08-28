# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: TestSign.test_nanopub_sign_bnode (lines 557-570, band high)
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

def test_nanopub_sign_bnode(self):
    expected_trusty = "RAcU1AR3dS0ricV5G_ENcpUCk40XuCvFW3tVFqxNEQzT4"
    assertion = Graph()
    assertion.add(
        (
            BNode("test"),
            namespaces.HYCL.claims,
            Literal("This is a test of nanopub-python"),
        )
    )
    np = Nanopub(conf=default_conf, assertion=assertion)
    np.sign()
    assert np.has_valid_signature
    assert expected_trusty in np.source_uri

# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: TestSign.test_sign_errors (lines 458-499, band high)
# licence of the source repository: see meta.json
import pytest
from rdflib import BNode, Graph, Literal, URIRef, Dataset, DC, RDF, Namespace, DCTERMS, PROV, XSD
from nanopub import (
    Nanopub,
    NanopubConf,
    namespaces,
)
from nanopub.profile import ProfileError
from nanopub.utils import MalformedNanopubError
from conftest_context import (
    default_conf,
    profile_test,
    skip_if_nanopub_server_unavailable, testsuite, testsuite_conf,
)

def test_sign_errors(self, monkeypatch):
    # No profile -> should raise ProfileError
    np = Nanopub(conf=NanopubConf(profile=None))
    np._assertion.add(
        (URIRef("http://test"), namespaces.HYCL.claims, Literal("test claim"))
    )
    np._provenance.add(
        (
            np._assertion.identifier,
            PROV.wasAttributedTo,
            URIRef("http://someone"),
        )
    )
    np._pubinfo.add((np._metadata.namespace[""], DC.creator, Literal("tester")))

    with pytest.raises(ProfileError):
        np.sign()

    # Already signed -> should raise MalformedNanopubError
    np2 = Nanopub(conf=NanopubConf(profile=default_conf.profile))
    np2._assertion.add(
        (URIRef("http://test2"), namespaces.HYCL.claims, Literal("test claim 2"))
    )
    np2._provenance.add(
        (
            np2._assertion.identifier,
            PROV.wasAttributedTo,
            URIRef("http://someone"),
        )
    )
    np2._pubinfo.add((np2._metadata.namespace[""], DC.creator, Literal("tester")))
    np2._metadata.signature = True

    with pytest.raises(MalformedNanopubError):
        np2.sign()

    # Invalid nanopub -> should raise MalformedNanopubError
    monkeypatch.setattr(type(np2), "is_valid", property(lambda self: False))

    np2._metadata.signature = None
    with pytest.raises(MalformedNanopubError):
        np2.sign()

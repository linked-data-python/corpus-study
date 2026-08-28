# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: TestIllTypedLiterals.test_publish_rejects_ill_typed_literal_in_signed_nanopub (lines 874-894, band high)
# licence of the source repository: see meta.json
from unittest.mock import MagicMock, patch
import pytest
from rdflib import BNode, Graph, Literal, URIRef, Dataset, DC, RDF, Namespace, DCTERMS, PROV, XSD
from nanopub.utils import MalformedNanopubError
from tests.conftest import (
    default_conf,
    profile_test,
    skip_if_nanopub_server_unavailable, testsuite, testsuite_conf,
)
from test_nanopub_context import _minimal_valid_nanopub

def test_publish_rejects_ill_typed_literal_in_signed_nanopub(self, monkeypatch):
    """publish() used to run no validation at all on an already-signed nanopub, such as
    one read from a file or fetched from the registry."""
    np = _minimal_valid_nanopub(conf=default_conf)
    np.sign()
    np.pubinfo.add(
        (
            np._metadata.namespace[""],
            URIRef("http://example.org/count"),
            Literal("not-a-number", datatype=XSD.integer),
        )
    )
    # editing the graph after signing breaks the trusty artefact, which is not what
    # this test is about
    monkeypatch.setattr(type(np), "is_valid", property(lambda self: True))

    with patch("nanopub.nanopub.publish_graph") as mock_publish:
        with pytest.raises(MalformedNanopubError, match="not-a-number"):
            np.publish()
    mock_publish.assert_not_called()
    assert not np.published

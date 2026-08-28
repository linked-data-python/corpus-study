# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: TestSign.test_nanopub_sign_object_bnode (lines 594-614, band high)
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

def test_nanopub_sign_object_bnode(self):
    """Regression: a blank node in object position must not crash signing.

    ``_replace_blank_nodes`` referenced an undefined ``old_o`` in a debug log
    on the object branch, which raised ``NameError`` during ``sign()`` (the
    other ``sign_bnode`` tests only use blank nodes in subject position, so
    they never exercised this branch). The blank node should be rewritten to
    a concrete URI in the nanopub's namespace.
    """
    ex = Namespace("http://example.org/")
    assertion = Graph()
    bnode = BNode("objnode")
    # bnode appears in object position (first triple) and subject position
    # (second), mirroring real "introduce a structured value" assertions.
    assertion.add((ex.subject, ex.hasPart, bnode))
    assertion.add((bnode, RDF.type, ex.Part))
    np = Nanopub(conf=default_conf, assertion=assertion)
    np.sign()
    assert np.has_valid_signature
    # The object blank node was replaced by a concrete URI, none remain.
    assert not any(isinstance(o, BNode) for o in np.rdf.objects())

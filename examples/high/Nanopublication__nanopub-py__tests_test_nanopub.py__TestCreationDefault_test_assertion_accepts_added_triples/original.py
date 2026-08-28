# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: TestCreationDefault.test_assertion_accepts_added_triples (lines 116-120, band high)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, URIRef, Dataset, DC, RDF, Namespace, DCTERMS, PROV, XSD
from nanopub import (
    Nanopub,
    NanopubConf,
    namespaces,
)

def test_assertion_accepts_added_triples(self):
    """Triples added to assertion post-construction should be stored."""
    np = Nanopub(conf=NanopubConf())
    np.assertion.add((URIRef("http://another"), namespaces.HYCL.claims, Literal("hello")))
    assert len(np.assertion) == 1

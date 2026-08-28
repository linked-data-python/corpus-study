# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: TestHandleDerivedFrom.test_from_list (lines 714-720, band high)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, URIRef, Dataset, DC, RDF, Namespace, DCTERMS, PROV, XSD
from nanopub import (
    Nanopub,
    NanopubConf,
    namespaces,
)

def test_from_list(self):
    np = Nanopub(conf=NanopubConf())
    np._handle_derived_from(["http://example.org/derived2"])
    found2 = list(
        np.provenance.triples((None, None, URIRef("http://example.org/derived2")))
    )
    assert found2

# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: TestHandleIntroducesConcept.test_handle_introduces_concept_adds_triple (lines 733-738, band high)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, URIRef, Dataset, DC, RDF, Namespace, DCTERMS, PROV, XSD
from nanopub_shim import (
    Nanopub,
    NanopubConf,
    namespaces,
)

def test_handle_introduces_concept_adds_triple(self):
    np = Nanopub(conf=NanopubConf())
    bnode = BNode("concept1")
    np._handle_introduces_concept(bnode)
    triples = list(np.pubinfo.triples((None, None, None)))
    assert triples

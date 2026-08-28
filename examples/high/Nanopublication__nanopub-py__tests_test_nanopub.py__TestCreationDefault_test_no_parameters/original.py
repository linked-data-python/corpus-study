# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: TestCreationDefault.test_no_parameters (lines 86-92, band high)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, URIRef, Dataset, DC, RDF, Namespace, DCTERMS, PROV, XSD
from nanopub import (
    Nanopub,
    NanopubConf,
    namespaces,
)

def test_no_parameters(self):
    np = Nanopub()
    assert np.source_uri is None
    assert len(np.head) > 0
    assert len(list(np.head.triples((None, RDF.type, namespaces.NP.Nanopublication)))) == 1
    assert len(list(np.head.triples((None, namespaces.NP.hasProvenance, None)))) == 1
    assert len(list(np.head.triples((None, namespaces.NP.hasPublicationInfo, None)))) == 1

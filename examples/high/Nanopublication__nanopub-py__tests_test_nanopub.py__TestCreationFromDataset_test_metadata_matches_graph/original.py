# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: TestCreationFromDataset.test_metadata_matches_graph (lines 262-268, band high)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, URIRef, Dataset, DC, RDF, Namespace, DCTERMS, PROV, XSD
from nanopub import (
    Nanopub,
    NanopubConf,
    namespaces,
)

def test_metadata_matches_graph(self, testsuite):
    """Metadata np_uri should reflect the URI in the parsed trig."""
    ds = Dataset()
    ds.parse(data=testsuite.get_by_nanopub_uri("http://example.org/nanopub-validator-example/").path.read_text(),
             format="trig")
    np = Nanopub(rdf=ds, conf=NanopubConf())
    assert "http://example.org/nanopub-validator-example/" in str(np.metadata.np_uri)

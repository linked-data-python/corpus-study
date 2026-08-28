# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: TestCreationFromTrustyNanopub.test_get_source_uri_from_graph_returns_trusty (lines 388-394, band high)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, URIRef, Dataset, DC, RDF, Namespace, DCTERMS, PROV, XSD
from nanopub import (
    Nanopub,
    NanopubConf,
    namespaces,
)

def test_get_source_uri_from_graph_returns_trusty(self, testsuite):
    """get_source_uri_from_graph should extract the trusty URI from the head."""
    ds = Dataset()
    ds.parse(data=testsuite.get_by_nanopub_uri(
        "http://purl.org/np/RA1sViVmXf-W2aZW4Qk74KTaiD9gpLBPe2LhMsinHKKz8").path.read_text(), format="trig")
    np = Nanopub(rdf=ds, conf=NanopubConf())
    assert np.get_source_uri_from_graph == "http://purl.org/np/RA1sViVmXf-W2aZW4Qk74KTaiD9gpLBPe2LhMsinHKKz8"

# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: TestCreationFromTrustyNanopub.test_source_uri_resolved_from_trusty_dataset (lines 350-357, band high)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, URIRef, Dataset, DC, RDF, Namespace, DCTERMS, PROV, XSD
from nanopub import (
    Nanopub,
    NanopubConf,
    namespaces,
)

def test_source_uri_resolved_from_trusty_dataset(self, testsuite):
    """source_uri should be set from the trusty URI found in the graph."""
    ds = Dataset()
    ds.parse(data=testsuite.get_by_nanopub_uri(
        "http://purl.org/np/RA1sViVmXf-W2aZW4Qk74KTaiD9gpLBPe2LhMsinHKKz8").path.read_text(), format="trig")
    np = Nanopub(rdf=ds, conf=NanopubConf())
    assert np.source_uri == "http://purl.org/np/RA1sViVmXf-W2aZW4Qk74KTaiD9gpLBPe2LhMsinHKKz8"
    assert np.is_valid

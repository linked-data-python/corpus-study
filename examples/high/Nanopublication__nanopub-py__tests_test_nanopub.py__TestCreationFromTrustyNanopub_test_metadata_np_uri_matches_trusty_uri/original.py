# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: TestCreationFromTrustyNanopub.test_metadata_np_uri_matches_trusty_uri (lines 368-375, band high)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, URIRef, Dataset, DC, RDF, Namespace, DCTERMS, PROV, XSD
from nanopub import (
    Nanopub,
    NanopubConf,
    namespaces,
)

def test_metadata_np_uri_matches_trusty_uri(self, testsuite):
    """Metadata np_uri should match the trusty URI declared in the graph."""
    ds = Dataset()
    ds.parse(data=testsuite.get_by_nanopub_uri(
        "http://purl.org/np/RA1sViVmXf-W2aZW4Qk74KTaiD9gpLBPe2LhMsinHKKz8").path.read_text(), format="trig")
    np = Nanopub(rdf=ds, conf=NanopubConf())
    assert str(np.metadata.np_uri) == "http://purl.org/np/RA1sViVmXf-W2aZW4Qk74KTaiD9gpLBPe2LhMsinHKKz8"
    assert np.is_valid

# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: TestCreationFromTrustyNanopub.test_all_sub_graphs_non_empty (lines 377-386, band high)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, URIRef, Dataset, DC, RDF, Namespace, DCTERMS, PROV, XSD
from nanopub import (
    Nanopub,
    NanopubConf,
    namespaces,
)

def test_all_sub_graphs_non_empty(self, testsuite):
    """All four sub-graphs should be populated from a trusty trig."""
    ds = Dataset()
    ds.parse(data=testsuite.get_by_nanopub_uri(
        "http://purl.org/np/RA1sViVmXf-W2aZW4Qk74KTaiD9gpLBPe2LhMsinHKKz8").path.read_text(), format="trig")
    np = Nanopub(rdf=ds, conf=NanopubConf())
    assert len(np.head) > 0
    assert len(np.assertion) > 0
    assert len(np.provenance) > 0
    assert len(np.pubinfo) > 0

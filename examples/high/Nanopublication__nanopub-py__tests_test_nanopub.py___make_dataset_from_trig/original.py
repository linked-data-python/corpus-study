# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: _make_dataset_from_trig (lines 26-29, band high)
# licence of the source repository: see meta.json
from nanopub_testsuite_connector import TestSuiteSubfolder
from rdflib import BNode, Graph, Literal, URIRef, Dataset, DC, RDF, Namespace, DCTERMS, PROV, XSD

def _make_dataset_from_trig(testsuite) -> Dataset:
    ds = Dataset()
    ds.parse(testsuite.get_valid(TestSuiteSubfolder.PLAIN)[0].path, format="trig")
    return ds

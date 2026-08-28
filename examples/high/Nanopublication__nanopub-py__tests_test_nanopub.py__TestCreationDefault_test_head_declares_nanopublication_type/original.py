# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: TestCreationDefault.test_head_declares_nanopublication_type (lines 99-102, band high)
# licence of the source repository: see meta.json
import nanopub_shim  # noqa: F401  context shim, see meta.json
from rdflib import BNode, Graph, Literal, URIRef, Dataset, DC, RDF, Namespace, DCTERMS, PROV, XSD
from nanopub import (
    Nanopub,
    NanopubConf,
    namespaces,
)

def test_head_declares_nanopublication_type(self):
    """Head should declare the np:Nanopublication type triple."""
    np = Nanopub(conf=NanopubConf())
    assert len(list(np.head.triples((None, RDF.type, namespaces.NP.Nanopublication)))) == 1

# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: _simple_assertion (lines 47-50, band high)
# licence of the source repository: see meta.json
import nanopub_shim  # noqa: F401  context shim, see meta.json
from rdflib import BNode, Graph, Literal, URIRef, Dataset, DC, RDF, Namespace, DCTERMS, PROV, XSD
from nanopub import (
    Nanopub,
    NanopubConf,
    namespaces,
)

def _simple_assertion() -> Graph:
    g = Graph()
    g.add((URIRef("http://test"), namespaces.HYCL.claims, Literal("test claim")))
    return g

# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: TestCreationDefault.test_introduces_concept_multiple_error (lines 168-177, band high)
# licence of the source repository: see meta.json
import pytest
from rdflib import BNode, Graph, Literal, URIRef, Dataset, DC, RDF, Namespace, DCTERMS, PROV, XSD
from nanopub import (
    Nanopub,
    NanopubConf,
    namespaces,
)
from nanopub.utils import MalformedNanopubError

def test_introduces_concept_multiple_error(self):
    np = Nanopub(conf=NanopubConf())
    np._pubinfo.add(
        (URIRef("http://s"), namespaces.NPX.introduces, URIRef("http://c1"))
    )
    np._pubinfo.add(
        (URIRef("http://s"), namespaces.NPX.introduces, URIRef("http://c2"))
    )
    with pytest.raises(MalformedNanopubError):
        np.introduces_concept

# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: TestIllTypedLiterals.test_ill_typed_literal_parsed_from_trig (lines 829-841, band high)
# licence of the source repository: see meta.json
import pytest
from rdflib import BNode, Graph, Literal, URIRef, Dataset, DC, RDF, Namespace, DCTERMS, PROV, XSD
from nanopub import (
    Nanopub,
    NanopubConf,
    namespaces,
)
from nanopub.utils import MalformedNanopubError

def test_ill_typed_literal_parsed_from_trig(self):
    np = _minimal_valid_nanopub()
    np.assertion.add(
        (
            URIRef("http://test"),
            URIRef("http://example.org/count"),
            Literal("not-a-number", datatype=XSD.integer),
        )
    )
    ds = Dataset()
    ds.parse(data=np.serialize(format="trig"), format="trig")
    with pytest.raises(MalformedNanopubError, match="not-a-number"):
        Nanopub(conf=NanopubConf(), rdf=ds).is_valid

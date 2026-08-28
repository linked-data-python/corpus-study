# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: TestIllTypedLiterals.test_ill_typed_literal_in_pubinfo (lines 796-809, band high)
# licence of the source repository: see meta.json
import pytest
from rdflib import BNode, Graph, Literal, URIRef, Dataset, DC, RDF, Namespace, DCTERMS, PROV, XSD
from nanopub.utils import MalformedNanopubError

def test_ill_typed_literal_in_pubinfo(self):
    np = _minimal_valid_nanopub()
    np.pubinfo.add(
        (
            np._metadata.namespace[""],
            DCTERMS.created,
            Literal("yesterday", datatype=XSD.dateTime),
        )
    )
    literals = np.ill_typed_literals
    assert [str(o) for o, _ in literals] == ["yesterday"]
    assert str(literals[0][1]) == str(np.pubinfo.identifier)
    with pytest.raises(MalformedNanopubError, match="yesterday"):
        np.is_valid

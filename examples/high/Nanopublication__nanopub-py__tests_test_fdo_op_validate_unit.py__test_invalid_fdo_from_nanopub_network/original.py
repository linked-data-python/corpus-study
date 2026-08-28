# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_fdo_op_validate_unit.py
# region: test_invalid_fdo_from_nanopub_network (lines 182-222, band high)
# licence of the source repository: see meta.json
from unittest.mock import patch, MagicMock
from rdflib import URIRef, Graph, Literal, BNode
from rdflib.namespace import DCTERMS, RDF, SH, XSD
from nanopub.fdo.fdo_record import FdoRecord
from nanopub.fdo.validate import validate_fdo_record
from nanopub.namespaces import FDOF

@patch("nanopub.fdo.validate.requests.get")
@patch("nanopub.fdo.validate.resolve_in_nanopub_network")
def test_invalid_fdo_from_nanopub_network(mock_resolve, mock_get):
    record_graph = Graph()
    subject = URIRef("https://example.org/fdo/2")
    record_graph.add((subject, RDF.type, FDOF.FAIRDigitalObject))
    record_graph.add((subject, DCTERMS.conformsTo, URIRef("https://hdl.handle.net/21.T11966/996c38676da9ee56f8ab")))
    fdo_record_nanopub = MagicMock()
    fdo_record_nanopub.assertion = record_graph

    profile_graph = Graph()
    profile_uri = URIRef("https://hdl.handle.net/21.T11966/996c38676da9ee56f8ab")

    shape = BNode()
    profile_graph.add((shape, RDF.type, SH.NodeShape))
    profile_graph.add((shape, SH.targetClass, FDOF.FAIRDigitalObject))

    property_bnode = BNode()
    profile_graph.add((shape, SH.property, property_bnode))
    profile_graph.add((property_bnode, SH.path, URIRef("https://example.org/predicate")))
    profile_graph.add((property_bnode, SH.minCount, Literal(2, datatype=XSD.integer)))
    profile_graph.add((property_bnode, SH.maxCount, Literal(1)))

    fdo_profile_nanopub = MagicMock()
    fdo_profile_nanopub.assertion = profile_graph

    def resolve_side_effect(uri):
        if str(uri) == str(subject):
            return fdo_record_nanopub
        elif str(uri) == str(profile_uri):
            return fdo_profile_nanopub
        return None

    mock_resolve.side_effect = resolve_side_effect
    mock_get.return_value = MagicMock(status_code=404)

    record = FdoRecord(assertion=record_graph)
    result = validate_fdo_record(record)

    assert result.is_valid is False
    assert len(result.errors) > 0


# --- demo harness (added identically to both representations; see meta.json) ---
# The region is a pytest test: it returns nothing and keeps both graphs in
# locals, so on its own it offers the driver nothing beyond "it did not raise".
# Wrapping MagicMock captures the two assertion graphs it builds and
# republishes them at module level, where the driver compares them.
_captured = []
_MagicMock = MagicMock


def MagicMock(*args, **kwargs):
    _mock = _MagicMock(*args, **kwargs)
    _captured.append(_mock)
    return _mock


def _assertion_graph_of(_mock):
    # MagicMock rejects attribute names starting with "assert" unless they
    # were explicitly set, so a plain getattr is not enough here.
    try:
        _value = _mock.assertion
    except AttributeError:
        return None
    return _value if isinstance(_value, Graph) else None


test_invalid_fdo_from_nanopub_network()

record_graph, profile_graph = [
    _g for _g in map(_assertion_graph_of, _captured) if _g is not None
]

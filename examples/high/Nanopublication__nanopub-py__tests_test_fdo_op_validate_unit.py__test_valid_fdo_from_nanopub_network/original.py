# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_fdo_op_validate_unit.py
# region: test_valid_fdo_from_nanopub_network (lines 138-179, band high)
# licence of the source repository: see meta.json
from unittest.mock import patch, MagicMock
from rdflib import URIRef, Graph, Literal, BNode
from rdflib.namespace import DCTERMS, RDF, SH, XSD
from nanopub.fdo.fdo_record import FdoRecord
from nanopub.fdo.validate import validate_fdo_record
from nanopub.namespaces import FDOF
HANDLE_METADATA = {
    "responseCode": 1,
    "handle": "21.T11966/996c38676da9ee56f8ab",
    "values": [
        {
            "index": 3,
            "type": "21.T11966/JsonSchema",
            "data": {
                "format": "string",
                "value": '{"$ref": "https://example.org/schema/fdo.json"}',
            },
        }
    ],
}

@patch("nanopub.fdo.validate.requests.get")
@patch("nanopub.fdo.validate.resolve_in_nanopub_network")
def test_valid_fdo_from_nanopub_network(mock_resolve, mock_get):
    record_graph = Graph()
    subject = URIRef("https://example.org/fdo/1")
    record_graph.add((subject, RDF.type, FDOF.FAIRDigitalObject))
    record_graph.add((subject, URIRef("https://example.org/predicate"), Literal("Value")))
    record_graph.add((subject, DCTERMS.conformsTo, URIRef("https://hdl.handle.net/21.T11966/996c38676da9ee56f8ab")))
    fdo_record_nanopub = MagicMock()
    fdo_record_nanopub.assertion = record_graph

    profile_graph = Graph()
    profile_uri = URIRef("https://hdl.handle.net/21.T11966/996c38676da9ee56f8ab")

    shape = BNode()
    property_bnode = BNode()

    profile_graph.add((shape, RDF.type, SH.NodeShape))
    profile_graph.add((shape, SH.targetClass, FDOF.FAIRDigitalObject))
    profile_graph.add((shape, SH.property, property_bnode))
    profile_graph.add((property_bnode, SH.path, URIRef("https://example.org/predicate")))
    profile_graph.add((property_bnode, SH.minCount, Literal(1, datatype=XSD.integer)))
    profile_graph.add((property_bnode, SH.maxCount, Literal(1, datatype=XSD.integer)))

    fdo_profile_nanopub = MagicMock()
    fdo_profile_nanopub.assertion = profile_graph

    def resolve_side_effect(uri):
        if str(uri) == str(subject):
            return fdo_record_nanopub
        elif str(uri) == str(profile_uri):
            return fdo_profile_nanopub
        return None

    mock_resolve.side_effect = resolve_side_effect
    mock_get.return_value = MagicMock(status_code=200, json=lambda: HANDLE_METADATA)

    record = FdoRecord(assertion=record_graph)
    result = validate_fdo_record(record)

    assert result.is_valid is True
    assert result.errors == []

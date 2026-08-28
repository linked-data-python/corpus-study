# Extracted from statnett/KGraphPy@38859be62f : tests/test_header_validation.py
# region: test__fix_trig_period_of_time_format_periodoftimeremoval (lines 811-838, stratum add_isolated)
# licence of the source repository: see meta.json
import pytest
from unittest.mock import call, patch, MagicMock
from rdflib import BNode, Graph, Literal, Node, URIRef
from rdflib.namespace import XSD, DCAT, DCTERMS, RDF
from kgraphpy.header_validation import (
    _check_dcterms_issued_count, 
    _check_trig_rdfg_graph,
    _correct_triple_representation_by_predicate,
    _make_bnode_triple_for_given_predicate,
    _remove_cimxml_rdfg_graph,
    _remove_cimxml_rdfg_graph, 
    _remove_invalid_triples, 
    _fix_datetime_format_in_triples, 
    _fix_datetime_format,
    _fix_cimxml_period_of_time_format,
    _fix_trig_period_of_time_format,
    validate_header
)

@pytest.mark.parametrize(
    "occurences",
    [
        pytest.param(0, id="No temporal triple"),
        pytest.param(1, id="One temporal triple"),
        pytest.param(2, id="Two temporal triples"),
    ]
)
@patch("kgraphpy.header_validation._make_bnode_triple_for_given_predicate")
def test__fix_trig_period_of_time_format_periodoftimeremoval(mock_make_bnode: MagicMock, occurences: int) -> None:
    g = Graph()
    id = URIRef("id1")
    g.add((id, DCAT.startDate, Literal("2025-02-14T00:00:00+00:00")))
    for i in range(occurences):
        g.add((URIRef(f"s{i}"), RDF.type, DCTERMS.PeriodOfTime))

    _fix_trig_period_of_time_format(g, id)

    assert len(g) == 3

    temporal_triple = list(g.triples((id, DCTERMS.temporal, None)))
    assert len(temporal_triple) == 1
    assert temporal_triple[0] in g
    bnode = temporal_triple[0][2]
    assert (bnode, RDF.type, DCTERMS.PeriodOfTime) in g
    mock_make_bnode.assert_has_calls([call(g, bnode, DCAT.endDate), call(g, bnode, DCAT.startDate)], any_order=True)
    for i in range(occurences):
        assert (URIRef(f"s{i}"), RDF.type, DCTERMS.PeriodOfTime) not in g

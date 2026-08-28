# Extracted from statnett/KGraphPy@38859be62f : tests/test_header_validation.py
# region: test__fix_trig_period_of_time_format_nodatetriples (lines 763-779, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
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

@patch("kgraphpy.header_validation._make_bnode_triple_for_given_predicate")
def test__fix_trig_period_of_time_format_nodatetriples(mock_make_bnode: MagicMock) -> None:
    g = Graph()
    id = URIRef("id1")
    g.add((id, RDF.type, DCAT.Dataset))
    g.add((id, DCTERMS.temporal, URIRef("o1")))
    g.add((id, RDF.type, DCTERMS.PeriodOfTime))

    _fix_trig_period_of_time_format(g, id)

    assert len(g) == 1

    temporal_triple = list(g.triples((id, DCTERMS.temporal, None)))
    assert len(temporal_triple) == 0
    assert (id, RDF.type, DCAT.Dataset) in g
    assert (id, RDF.type, DCTERMS.PeriodOfTime) not in g
    mock_make_bnode.assert_not_called()

# Extracted from statnett/KGraphPy@38859be62f : tests/test_header_validation.py
# region: test_fix_cimxml_period_of_time_format_periodoftime (lines 634-658, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
import pytest
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
        pytest.param(0, id="No periodOfTime triple"),
        pytest.param(1, id="One periodOfTime triple"),
        pytest.param(2, id="Two periodOfTime triples"),
    ]
)
def test_fix_cimxml_period_of_time_format_periodoftime(occurences: int) -> None:
    g = Graph()
    id = URIRef("id1")
    g.add((id, DCTERMS.conformsTo, Literal("whatever")))
    g.add((id, DCAT.endDate, Literal("2025-02-14T00:00:00+00:00")))
    g.add((id, DCAT.startDate, Literal("2025-02-01T00:00:00+00:00")))
    for i in range(occurences):
        g.add((URIRef(f"s{i}"), RDF.type, DCTERMS.PeriodOfTime))

    _fix_cimxml_period_of_time_format(g, id)

    assert (id, DCTERMS.conformsTo, Literal("whatever")) in g
    assert (id, DCAT.endDate, Literal("2025-02-14T00:00:00+00:00")) in g
    assert (id, DCAT.startDate, Literal("2025-02-01T00:00:00+00:00")) in g
    assert len(g) == 3
    for i in range(occurences):
        assert (URIRef(f"s{i}"), RDF.type, DCTERMS.PeriodOfTime) not in g

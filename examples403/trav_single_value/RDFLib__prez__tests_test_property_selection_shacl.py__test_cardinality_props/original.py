# Extracted from RDFLib/prez@421ee0a9fe : tests/test_property_selection_shacl.py
# region: test_cardinality_props (lines 227-261, stratum trav_single_value)
# licence of the source repository: see meta.json
import pytest
from rdflib import DCTERMS, PROV, RDF, SH, Graph, URIRef, SKOS
from sparql_grammar_pydantic import (
    IRI,
    Filter,
    GroupOrUnionGraphPattern,
    OptionalGraphPattern,
    TriplesSameSubject,
    TriplesSameSubjectPath,
    Var,
)
from prez.services.query_generation.shacl import PropertyShape

@pytest.mark.parametrize(
    ["cardinality_type", "expected_result"],
    [
        (
            "sh:zeroOrMorePath",
            "?focus_node <http://purl.org/dc/terms/publisher>* ?prof_1_node_1",
        ),
        (
            "sh:oneOrMorePath",
            "?focus_node <http://purl.org/dc/terms/publisher>+ ?prof_1_node_1",
        ),
        (
            "sh:zeroOrOnePath",
            "?focus_node <http://purl.org/dc/terms/publisher>? ?prof_1_node_1",
        ),
    ],
)
def test_cardinality_props(cardinality_type, expected_result):
    g = Graph().parse(
        data=f"""
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX sh: <http://www.w3.org/ns/shacl#>

    <http://example-profile> sh:property [
        sh:path [ {cardinality_type} dcterms:publisher ] ;
        ]
    .

    """
    )
    path_bn = g.value(subject=URIRef("http://example-profile"), predicate=SH.property)
    ps = PropertyShape(
        uri=path_bn, graph=g, kind="profile", focus_node=Var(value="focus_node")
    )
    assert ps.tssp_list[0].to_string() == expected_result

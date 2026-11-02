# Extracted from statnett/KGraphPy@38859be62f : tests/test_jsonld_utilities.py
# region: test_enrich_graph_datatypes_typecoercion (lines 301-313, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib import URIRef, Graph, Literal
from rdflib import XSD
from kgraphpy_shim import (
    reorder_jsonld, 
    sort_subjects, 
    sort_predicates, 
    load_json_from_url,
    extract_datatype_map,
    enrich_graph_datatypes
)

def test_enrich_graph_datatypes_typecoercion() -> None:
    g = Graph()
    g.bind("ex", "http://example.com/")
    g.add((URIRef("http://example.com/age"), URIRef("http://example.com/hasAge"), Literal(30.0, datatype=XSD.float)))
    g.add((URIRef("http://example.com/duration"), URIRef("http://example.com/hasAge"), Literal("not-a-number", datatype=None)))
    dt_map = {
        "http://example.com/hasAge": XSD.integer
    }

    enrich_graph_datatypes(g, dt_map)

    assert (URIRef("http://example.com/age"), URIRef("http://example.com/hasAge"), Literal(30.0, datatype=XSD.integer)) in g
    assert (URIRef("http://example.com/duration"), URIRef("http://example.com/hasAge"), Literal("not-a-number", datatype=XSD.integer)) in g

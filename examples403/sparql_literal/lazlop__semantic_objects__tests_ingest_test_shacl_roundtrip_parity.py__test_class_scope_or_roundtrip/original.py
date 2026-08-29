# Extracted from lazlop/semantic_objects@243c5efd8c : tests/ingest/test_shacl_roundtrip_parity.py
# region: test_class_scope_or_roundtrip (lines 162-190, stratum sparql_literal)
# licence of the source repository: see meta.json
# `semantic_objects.s223._generated` is not installable here (see _context.py);
# `_context` stands in for it and for the test file's own `_shacl_graph()`.
from _context import entities, properties, _shacl_graph

def test_class_scope_or_roundtrip():
    # Battery.connection_point: Union[OutletConnectionPoint_Electricity,
    # BidirectionalConnectionPoint_Electricity], ingested from a class-level
    # sh:or (BatteryCPShape, reached via sh:targetClass, not Battery's own
    # sh:property) combining two independent qualified property shapes -
    # round-trips as a NodeShape-level sh:or on Battery itself, each branch
    # its own sh:property with its own sh:qualifiedValueShape (including the
    # nested medium pin), not a single shared property shape.
    g = _shacl_graph(entities.Battery)
    assert not bool(g.query("ASK { s223:Battery sh:property ?p . }")), (
        "Battery has no direct sh:property of its own - only branches "
        "reachable through the class-level sh:or (each branch's own "
        "hasConnectionPoint path shape is checked separately below)"
    )
    result = g.query("""
        SELECT ?target WHERE {
            s223:Battery sh:or/rdf:rest*/rdf:first/sh:property ?prop .
            ?prop sh:path s223:hasConnectionPoint ;
                  sh:qualifiedMinCount ?min ;
                  sh:qualifiedValueShape [ sh:class ?target ;
                                            sh:node [ sh:property [ sh:path s223:hasMedium ;
                                                                     sh:class s223:Constituent-Electricity ] ] ] .
        }
    """)
    targets = {str(row.target) for row in result}
    assert targets == {
        'http://data.ashrae.org/standard223#OutletConnectionPoint',
        'http://data.ashrae.org/standard223#BidirectionalConnectionPoint',
    }
    # Appended (see meta.json): the original test asserts and returns nothing,
    # so the two versions would have nothing for the driver to compare beyond
    # "did not raise". Returning the computed set gives it something real.
    return targets

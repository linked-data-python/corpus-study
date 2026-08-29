# Extracted from hidden-graph/rdflib-starlight@b7973da2b5 : tests/unit/test_result_patches.py
# region: TestOrdinaryQueriesUnaffected.test_construct_query_still_works (lines 75-79, stratum sparql_interpolated)
# licence of the source repository: see meta.json
EX_A = "<http://example/a>"
EX_B = "<http://example/b>"
EX_C = "<http://example/c>"

def test_construct_query_still_works(self) -> None:
    g = _graph_with_one_fact()
    r = g.query(f"CONSTRUCT {{ {EX_A} {EX_B} {EX_C} . }} WHERE {{ {EX_A} {EX_B} {EX_C} . }}")
    triples = list(r)
    assert len(triples) == 1

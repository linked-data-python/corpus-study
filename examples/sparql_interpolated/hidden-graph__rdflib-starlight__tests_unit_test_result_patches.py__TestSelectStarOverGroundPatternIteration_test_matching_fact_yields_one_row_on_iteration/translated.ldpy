# Extracted from hidden-graph/rdflib-starlight@b7973da2b5 : tests/unit/test_result_patches.py
# region: TestSelectStarOverGroundPatternIteration.test_matching_fact_yields_one_row_on_iteration (lines 24-29, stratum sparql_interpolated)
# licence of the source repository: see meta.json
EX_A = "<http://example/a>"
EX_B = "<http://example/b>"
EX_C = "<http://example/c>"

def test_matching_fact_yields_one_row_on_iteration(self) -> None:
    g = _graph_with_one_fact()
    r = g.query(f"SELECT * WHERE {{ {EX_A} {EX_B} {EX_C} . }}")
    rows = list(r)
    assert len(rows) == 1
    assert tuple(rows[0]) == ()

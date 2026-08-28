# Extracted from hidden-graph/rdflib-starlight@b7973da2b5 : tests/unit/test_result_patches.py
# region: TestSelectStarOverGroundPatternIteration.test_nonmatching_fact_yields_zero_rows (lines 43-48, stratum sparql_interpolated)
# licence of the source repository: see meta.json
EX_A = "<http://example/a>"
EX_B = "<http://example/b>"
EX_NOPE = "<http://example/nope>"

def test_nonmatching_fact_yields_zero_rows(self) -> None:
    g = _graph_with_one_fact()
    r = g.query(f"SELECT * WHERE {{ {EX_A} {EX_B} {EX_NOPE} . }}")
    assert list(r) == []
    assert r.bindings == []
    assert len(r) == 0

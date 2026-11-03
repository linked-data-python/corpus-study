# Extracted from hidden-graph/rdflib-starlight@b7973da2b5 : tests/unit/test_result_patches.py
# region: TestSelectStarOverGroundPatternIteration.test_nonmatching_fact_yields_zero_rows (lines 43-48, stratum sparql_interpolated)
# licence of the source repository: see meta.json
#
# Context restored (see meta.json): `_graph_with_one_fact()`, defined at
# module scope in the real file but outside the extracted line range, is
# imported from graph_shim.py (a context shim) instead of being retyped
# here, so both representations call the identical helper.
from graph_shim import _graph_with_one_fact

EX_A = "<http://example/a>"
EX_B = "<http://example/b>"
EX_NOPE = "<http://example/nope>"

def test_nonmatching_fact_yields_zero_rows(self) -> None:
    r = _graph_with_one_fact().query(f"SELECT * WHERE {{ {EX_A} {EX_B} {EX_NOPE} . }}")
    assert list(r) == []
    assert r.bindings == []
    assert len(r) == 0

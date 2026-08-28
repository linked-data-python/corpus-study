# Extracted from hidden-graph/rdflib-starlight@b7973da2b5 : tests/unit/test_result_patches.py
# region: TestSelectStarOverGroundPatternIteration.test_matching_fact_agrees_with_ask (lines 38-41, stratum sparql_interpolated)
# licence of the source repository: see meta.json
from starlight_shim import _graph_with_one_fact  # context shim, see meta.json

EX_A = "<http://example/a>"
EX_B = "<http://example/b>"
EX_C = "<http://example/c>"

def test_matching_fact_agrees_with_ask(self) -> None:
    g = _graph_with_one_fact()
    ask = g.query(f"ASK {{ {EX_A} {EX_B} {EX_C} . }}")
    assert ask.askAnswer is True

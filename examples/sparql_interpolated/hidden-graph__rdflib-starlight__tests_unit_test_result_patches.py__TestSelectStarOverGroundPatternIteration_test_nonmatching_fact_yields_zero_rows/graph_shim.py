# Context shim (see meta.json): subset of
# tests/unit/test_result_patches.py from hidden-graph/rdflib-starlight
# @b7973da2b5, so the region executes outside the test module. The region
# calls `_graph_with_one_fact()`, defined at module scope alongside the test
# class but outside the extracted line range; restored here verbatim,
# together with the constants it needs (`EX_A`, `EX_B` are already restored
# in original.py/translated.ldpy for the query itself; `EX_C` is only used
# here, since the extracted context lines did not capture it -- this
# particular test does not reference `EX_C` directly, but the helper does).
# Identical bindings for both representations.
from rdflib import Graph

EX_A = "<http://example/a>"
EX_B = "<http://example/b>"
EX_C = "<http://example/c>"


def _graph_with_one_fact() -> Graph:
    g = Graph()
    g.parse(data=f"{EX_A} {EX_B} {EX_C} .", format="nt")
    return g

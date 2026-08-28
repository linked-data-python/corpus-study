"""Validation driver: the region is a pytest method; `self` is unused by it.

Nothing is returned and no argument is mutated: the four `pytest.raises`
blocks inside the region are the check, and they run on both sides.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry="test_is_valid_empty_graphs_and_graph_count",
                   calls=[lambda: ((None,), {})])

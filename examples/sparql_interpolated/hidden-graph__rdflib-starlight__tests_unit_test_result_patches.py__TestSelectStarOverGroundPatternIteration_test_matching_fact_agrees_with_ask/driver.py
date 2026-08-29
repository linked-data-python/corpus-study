"""Validation driver for hidden-graph__rdflib-starlight__tests_unit_test_result_patches.py__TestSelectStarOverGroundPatternIteration_test_matching_fact_agrees_with_ask.

The region body has no `self` reads (it is a bare test function that
happens to take an unused `self` parameter), so the driver calls it with a
placeholder `None`. See meta.json and starlight_shim.py for the resolved
`_graph_with_one_fact` helper the region depends on.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='test_matching_fact_agrees_with_ask',
    calls=[
        lambda: ((None,), {}),  # self is unused in the region body
    ],
)

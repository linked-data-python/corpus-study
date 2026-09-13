"""Validation driver for hidden-graph__rdflib-starlight__tests_unit_test_result_patches.py__TestSelectStarOverGroundPatternIteration_test_nonmatching_fact_yields_zero_rows.

Establishes semantic equivalence of original.py and translated.ldpy.

The region is a bound test method whose body never uses `self`, so a plain
`None` stands in for it; the region has nothing to return or mutate and
prints nothing, but this call argument makes `run_pair` treat it as
observed rather than "nothing observable to compare".
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='test_nonmatching_fact_yields_zero_rows',
    calls=[((None,), {})],
)

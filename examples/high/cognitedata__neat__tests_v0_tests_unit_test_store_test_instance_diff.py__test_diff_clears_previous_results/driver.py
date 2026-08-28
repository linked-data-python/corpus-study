"""Validation driver: the region is a pytest test taking no argument.

It builds a store, runs two diffs and asserts on the DIFF_ADD/DIFF_DELETE
named graphs, so calling it on both sides exercises every term the
translation rewrites (an assertion failure on either side surfaces as an
error in the verdict).
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='test_diff_clears_previous_results',
    calls=[lambda: ((), {})],
)

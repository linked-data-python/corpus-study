"""Validation driver: the region is a pytest test taking no argument.

It fills two named graphs, diffs them and asserts on the DIFF_ADD/DIFF_DELETE
graphs, so calling it on both sides exercises every term the translation
rewrites (an assertion failure on either side surfaces as an error in the
verdict).
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='test_diff_instances',
    calls=[lambda: ((), {})],
)

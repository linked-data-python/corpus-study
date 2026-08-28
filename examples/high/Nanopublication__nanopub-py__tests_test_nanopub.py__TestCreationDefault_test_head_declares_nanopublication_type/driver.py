"""Validation driver: the region is a pytest method; `self` is unused by it.

The region has no return value and mutates nothing observable from outside —
its own asserts are the check, and they run on both sides.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry="test_head_declares_nanopublication_type",
                   calls=[lambda: ((None,), {})])

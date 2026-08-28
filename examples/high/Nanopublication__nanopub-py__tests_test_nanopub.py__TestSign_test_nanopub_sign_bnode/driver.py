"""Validation driver: the region is a pytest method; `self` is unused by it.

Nothing is returned; the region's own asserts (valid signature, and the
expected trusty artifact code, which depends on every triple of the nanopub)
are the check, and they run on both sides.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry="test_nanopub_sign_bnode",
                   calls=[lambda: ((None,), {})])

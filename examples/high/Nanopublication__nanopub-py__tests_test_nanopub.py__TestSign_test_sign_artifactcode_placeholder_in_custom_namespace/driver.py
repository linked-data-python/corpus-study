"""Validation driver: the region is a pytest method taking the `testsuite`
fixture; `self` is unused.

The fixture is the shim's singleton test-suite object, so both sides receive
the very same object and the harness's argument comparison is trivially
satisfied; the region's own asserts (valid signature, valid trusty code, the
minted concept IRI present, no placeholder left) are the real check.
"""
from rdfeval.harness import run_pair

from conftest_shim import testsuite

VERDICT = run_pair(__file__,
                   entry="test_sign_artifactcode_placeholder_in_custom_namespace",
                   calls=[lambda: ((None, testsuite), {})])

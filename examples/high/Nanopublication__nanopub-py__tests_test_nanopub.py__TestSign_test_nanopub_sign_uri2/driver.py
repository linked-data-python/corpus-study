"""Validation driver: the region is a pytest method whose only argument is self.

It builds a nanopub over the test-suite RSA key, signs it, and asserts both
that the signature verifies and that the resulting Trusty URI carries the
expected artifact code.  That code is a hash of the serialised nanopub, so the
assert is a strong check on the translation: any difference in the assertion
triple would change it.  `self` is unused, so a None stand-in is passed.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry="test_nanopub_sign_uri2",
                   calls=[lambda: ((None,), {})])

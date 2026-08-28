# Context shim (see meta.json): the `profile_test` fixture the region signs
# with, normally imported from tests/conftest.py of
# Nanopublication/nanopub-py@05022dc4bc.  The upstream conftest fetches a
# signing key from the online nanopub test suite
# (`NanopubTestSuite.get_latest()`), which needs the network and the
# `nanopub_testsuite_connector` package; here the same Profile is built with a
# locally generated RSA key instead.  The module is imported once, so both
# representations sign with the SAME key and must produce byte-identical
# signatures and the same trusty URI.
# Imported IDENTICALLY by original.py and translated.ldpy.
from nanopub.profile import Profile

profile_test = Profile(
    agent_id="https://orcid.org/0000-0000-0000-0000",
    name="Python Tests",
)

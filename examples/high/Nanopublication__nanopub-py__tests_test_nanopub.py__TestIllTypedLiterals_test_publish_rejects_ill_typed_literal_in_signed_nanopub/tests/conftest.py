# Offline context shim (see meta.json) for tests/conftest.py of
# Nanopublication/nanopub-py@05022dc4bc.  The real conftest calls
# NanopubTestSuite.get_latest() at import time (a GitHub download) and probes
# the nanopub test server over HTTP.  This stand-in keeps the same names and
# the same NanopubConf values, but takes the signing key from the copy of
# nanopub-testsuite vendored in ../testsuite/ and never touches the network.
# Used IDENTICALLY by original.py and translated.ldpy.
import os
import tempfile

import pytest

from nanopub import NanopubConf, load_profile
from nanopub_testsuite_connector import NanopubTestSuite

_suite = NanopubTestSuite.get_local()
_signing_key = _suite.get_signing_key("rsa-key1")


@pytest.fixture(scope="session")
def testsuite() -> NanopubTestSuite:
    return _suite


# The upstream fixture is skipped when the nanopub server is unreachable; in
# this offline harness it is always unavailable.  Neither region uses it —
# it is imported only because it appears in the region's import list.
skip_if_nanopub_server_unavailable = pytest.mark.skipif(
    True, reason='Nanopub server is unavailable'
)

# Create a temporary profile.yml file for testing (verbatim upstream).
profile_test_path = os.path.join(tempfile.mkdtemp(), "profile.yml")
profile_yaml = f"""orcid_id: https://orcid.org/0000-0000-0000-0000
name: Python Tests
public_key: {_signing_key.public_key}
private_key: {_signing_key.private_key}
introduction_nanopub_uri:
"""
with open(profile_test_path, "w") as f:
    f.write(profile_yaml)

profile_test = load_profile(profile_test_path)

default_conf = NanopubConf(
    profile=profile_test,
    use_test_server=True,
    add_prov_generated_time=False,
    add_pubinfo_generated_time=False,
    attribute_assertion_to_profile=True,
    attribute_publication_to_profile=True,
    assertion_attributed_to=None,
    publication_attributed_to=None,
    derived_from=None
)

testsuite_conf = NanopubConf(
    profile=profile_test,
    use_test_server=True,
    add_prov_generated_time=False,
    add_pubinfo_generated_time=False,
    attribute_assertion_to_profile=False,
    attribute_publication_to_profile=False,
)

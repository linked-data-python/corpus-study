# Context shim (see meta.json): tests/conftest.py of
# Nanopublication/nanopub-py@05022dc4bc, minus the two things that need the
# network.  Upstream, conftest downloads the nanopub test suite from GitHub
# at import time (only to obtain the "rsa-key1" signing key pair) and pings
# the nanopub test server to decide whether to skip some tests.  Here the
# rsa-key1 pair was copied next to this file from
# Nanopublication/nanopub-testsuite@main (transform/signed/rsa-key1/key,
# MIT), and the server probe is a constant.  The profile.yml contents and
# the two NanopubConf objects are verbatim from conftest.
# Used identically by original.py and translated.ldpy.
import os
import tempfile
from pathlib import Path

import pytest

from nanopub import NanopubConf, load_profile

_HERE = Path(__file__).resolve().parent


class _SigningKeyPair:
    """The two attributes conftest reads off a testsuite signing key pair."""

    private_key = _HERE / "id_rsa"
    public_key = _HERE / "id_rsa.pub"


_signing_key = _SigningKeyPair()


def testsuite():
    raise RuntimeError(
        "the nanopub test suite is not materialised for this example; the "
        "region under test does not use it"
    )


skip_if_nanopub_server_unavailable = pytest.mark.skipif(
    True, reason='Nanopub server is unavailable'
)

# Create a temporary profile.yml file for testing
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

# Context shim (see meta.json): tests/conftest.py of
# Nanopublication/nanopub-py@05022dc4bc, reduced to the five bindings the
# region's import block lists.
#
# Upstream, conftest.py calls NanopubTestSuite.get_latest(), which downloads
# github.com/Nanopublication/nanopub-testsuite over the network, takes the
# 'rsa-key1' signing key from it, writes a temporary profile.yml holding the
# two key *paths*, and reloads it through yatiml into a ProfileLoader (a
# Profile subclass).  Here the very same key pair is kept locally in rsa-key1/
# and handed straight to Profile(...), which is exactly what that YAML
# round-trip produces -- and it keeps the example offline.  default_conf and
# testsuite_conf are then the upstream NanopubConf literals, verbatim.
#
# `testsuite` (a pytest session fixture) and
# `skip_if_nanopub_server_unavailable` (a pytest.mark.skipif whose condition
# pings the nanopub test server at import time) are imported by the extracted
# region but never used by it; they are stand-ins here.
#
# Imported IDENTICALLY by original.py and translated.ldpy.
from pathlib import Path

import nanopub_shim  # noqa: F401  puts the nanopub checkout on sys.path

from nanopub import NanopubConf
from nanopub.profile import Profile

# rsa-key1/ : transform/signed/rsa-key1/key/{id_rsa,id_rsa.pub} of the
# Nanopublication test suite (MIT, (c) 2022 Tobias Kuhn) -- a published test
# key pair, copied verbatim.
_KEY_DIR = Path(__file__).resolve().parent / "rsa-key1"

profile_test = Profile(
    agent_id="https://orcid.org/0000-0000-0000-0000",
    name="Python Tests",
    public_key=_KEY_DIR / "id_rsa.pub",
    private_key=_KEY_DIR / "id_rsa",
    introduction_nanopub_uri=None,
)

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

# unused by this region (see header)
testsuite = None


def skip_if_nanopub_server_unavailable(fn):
    return fn

# Context shim (see meta.json): stand-in for tests/conftest.py of
# Nanopublication/nanopub-py@05022dc4bc.  The real conftest builds its profile
# from `nanopub_testsuite_connector`, which downloads the nanopub test suite
# from GitHub at import time -- not installed here, and not reproducible.
# This shim rebuilds the very same objects from the `rsa-key1` key pair, copied
# verbatim into this directory from
# nanopub-testsuite@main : transform/signed/rsa-key1/key/  (MIT, (c) 2022
# Tobias Kuhn).  Checked: signing with this key reproduces exactly the trusty
# artifact code the region asserts.
# Imported identically by original.py and translated.ldpy.
import nanopub_shim  # noqa: F401
from pathlib import Path

from nanopub import NanopubConf
from nanopub.profile import Profile

_HERE = Path(__file__).resolve().parent

profile_test = Profile(
    agent_id="https://orcid.org/0000-0000-0000-0000",
    name="Python Tests",
    public_key=_HERE / "id_rsa.pub",
    private_key=_HERE / "id_rsa",
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

# Names the region's import line pulls in but never uses; the real ones probe
# the live nanopub server / the downloaded suite.
testsuite = None
skip_if_nanopub_server_unavailable = None

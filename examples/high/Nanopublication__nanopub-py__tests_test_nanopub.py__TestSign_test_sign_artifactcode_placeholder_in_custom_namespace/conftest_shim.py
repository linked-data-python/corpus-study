# Context shim (see meta.json): stand-in for tests/conftest.py of
# Nanopublication/nanopub-py@05022dc4bc.  The real conftest and the `testsuite`
# fixture come from `nanopub_testsuite_connector`, which downloads the nanopub
# test suite from GitHub at import time -- not installed here, and not
# reproducible.  This shim rebuilds the same objects from three files copied
# verbatim from nanopub-testsuite@main (MIT, (c) 2022 Tobias Kuhn):
#   * transform/signed/rsa-key1/key/{id_rsa,id_rsa.pub}
#   * transform/plain/artifactcode-1.in.trig  (the only case the region uses)
# The `testsuite` object mirrors the connector's TransformTestCase/
# TestSuiteEntry API surface the region touches (.plain.name, .plain.read_text).
# Imported identically by original.py and translated.ldpy.
import nanopub_shim  # noqa: F401
from dataclasses import dataclass
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


@dataclass(frozen=True)
class _TestSuiteEntry:
    name: str
    path: Path

    def read_text(self, encoding: str = "utf-8") -> str:
        return self.path.read_text(encoding=encoding)


@dataclass(frozen=True)
class _TransformTestCase:
    key_name: str
    plain: _TestSuiteEntry


class _NanopubTestSuite:
    _CASES = [
        _TransformTestCase(
            key_name="rsa-key1",
            plain=_TestSuiteEntry(name="artifactcode-1.in.trig",
                                  path=_HERE / "artifactcode-1.in.trig"),
        ),
    ]

    def get_transform_cases(self, key_name=None):
        if key_name is None:
            return list(self._CASES)
        return [c for c in self._CASES if c.key_name == key_name]


testsuite = _NanopubTestSuite()

# Name the region's import line pulls in but never uses; the real one probes
# the live nanopub server.
skip_if_nanopub_server_unavailable = None

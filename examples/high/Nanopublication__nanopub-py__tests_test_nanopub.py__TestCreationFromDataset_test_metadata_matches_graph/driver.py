"""Validation driver: the region is a pytest method taking self and testsuite.

`testsuite` is the session fixture built by tests/conftest.py from the
nanopub test suite, which the connector downloads from GitHub.  The fixture
here is a stand-in exposing only `get_by_nanopub_uri`, pointing at the local
copy of the entry the real index returns for that URI (noprovlink.trig, see
meta.json).  `self` is unused by the region, so a None stand-in is passed.
"""
from pathlib import Path

from rdfeval.harness import run_pair

_HERE = Path(__file__).resolve().parent


class _Entry:
    """Stand-in for nanopub_testsuite_connector.TestSuiteEntry."""

    def __init__(self, path):
        self.path = path


class _TestSuite:
    """Stand-in for nanopub_testsuite_connector.NanopubTestSuite."""

    _INDEX = {
        "http://example.org/nanopub-validator-example/": _HERE / "noprovlink.trig",
    }

    def get_by_nanopub_uri(self, uri):
        return _Entry(self._INDEX[uri])

    def __eq__(self, other):  # the harness compares arguments after the call
        return isinstance(other, _TestSuite)


VERDICT = run_pair(__file__, entry="test_metadata_matches_graph",
                   calls=[lambda: ((None, _TestSuite()), {})])

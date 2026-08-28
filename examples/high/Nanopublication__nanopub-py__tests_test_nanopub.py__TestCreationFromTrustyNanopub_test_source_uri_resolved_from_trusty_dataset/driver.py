"""Validation driver for TestCreationFromTrustyNanopub.test_source_uri_resolved_from_trusty_dataset.

Context (identical for both representations):

* the ``nanopub`` package is not installed in the evaluation venv, so the
  corpus checkout Nanopublication/nanopub-py@05022dc4bc is put on sys.path
  before either module is executed (all of its dependencies — rdflib,
  requests, typer, yatiml, pycryptodome, SPARQLWrapper, pyshacl — are
  installed);
* the region's ``testsuite`` fixture is the nanopub test suite, normally
  downloaded from GitHub at import time by tests/conftest.py.  Only one
  entry is needed here, so ``example4.trig`` (the trusty nanopub
  http://purl.org/np/RA1sViVmXf-W2aZW4Qk74KTaiD9gpLBPe2LhMsinHKKz8) was
  copied next to this driver from Nanopublication/nanopub-testsuite@main
  (valid/trusty/example4.trig, MIT) and is served by the stand-in below.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE.parents[2] / "corpus" / "repos" / "Nanopublication__nanopub-py"
if str(CORPUS) not in sys.path:
    sys.path.insert(0, str(CORPUS))

from rdfeval.harness import run_pair  # noqa: E402


class TestSuiteEntry:
    """The two attributes the region uses of a nanopub_testsuite_connector entry."""

    def __init__(self, path):
        self.path = path

    def read_text(self, encoding="utf-8"):
        return self.path.read_text(encoding=encoding)


class TestSuiteStub:
    ENTRIES = {
        "http://purl.org/np/RA1sViVmXf-W2aZW4Qk74KTaiD9gpLBPe2LhMsinHKKz8":
            HERE / "example4.trig",
    }

    def get_by_nanopub_uri(self, uri):
        return TestSuiteEntry(self.ENTRIES[uri])

    def __eq__(self, other):
        return isinstance(other, TestSuiteStub)


def trusty_nanopub():
    return ((None, TestSuiteStub()), {})


VERDICT = run_pair(__file__, entry="test_source_uri_resolved_from_trusty_dataset",
                   calls=[trusty_nanopub])

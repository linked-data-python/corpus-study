"""Validation driver for Nanopublication__nanopub-py__tests_test_nanopub.py__TestCreationFromTrustyNanopub_test_metadata_np_uri_matches_trusty_uri.

The region takes its ``testsuite`` pytest fixture as a parameter, so no edit of
the two files is needed: the driver passes a stand-in whose
``get_by_nanopub_uri`` serves the one nanopub the test asks for, saved next to
this driver (fetched from its purl, see meta.json).  That keeps the real
``nanopub_testsuite_connector`` (and its network download) out of the loop.
The corpus checkout of commit 05022dc4bc is put on sys.path so the region's
``nanopub`` imports stay as upstream.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True

CORPUS = ("/home/lefrancois/Documents/recherche/semantic_web_micropython/github"
          "/corpus/repos/Nanopublication__nanopub-py")
if CORPUS not in sys.path:
    sys.path.insert(0, CORPUS)

from rdfeval.harness import run_pair  # noqa: E402

HERE = Path(__file__).resolve().parent
NP_URI = "http://purl.org/np/RA1sViVmXf-W2aZW4Qk74KTaiD9gpLBPe2LhMsinHKKz8"


class _Entry:
    def __init__(self, path):
        self.path = path


class _TestSuite:
    """Minimal stand-in for nanopub_testsuite_connector.NanopubTestSuite."""

    def get_by_nanopub_uri(self, uri):
        assert uri == NP_URI, "unexpected nanopub uri %r" % (uri,)
        return _Entry(HERE / (uri.rsplit("/", 1)[1] + ".trig"))


# one shared instance: the two fixture invocations must yield equal arguments
TESTSUITE = _TestSuite()


def call():
    return ((None, TESTSUITE), {})


VERDICT = run_pair(__file__, entry="test_metadata_np_uri_matches_trusty_uri",
                   calls=[call])

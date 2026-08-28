"""Validation driver: the test asserts that a trusty nanopub's source URI is
read back from its head graph.

The `nanopub` package is not installed in the evaluation venv; it is taken
from the corpus checkout by appending it to sys.path (appended, not
prepended, so the example's own shim modules keep priority).  The
`testsuite` fixture is supplied offline by the local
nanopub_testsuite_connector shim.
"""
import sys
from pathlib import Path

_CORPUS = (Path(__file__).resolve().parents[3]
           / "corpus" / "repos" / "Nanopublication__nanopub-py")
if str(_CORPUS) not in sys.path:
    sys.path.append(str(_CORPUS))

from nanopub_testsuite_connector import NanopubTestSuite  # noqa: E402
from rdfeval.harness import run_pair  # noqa: E402

TESTSUITE = NanopubTestSuite.get_local()


def trusty_nanopub():
    # (self, testsuite): the region does not touch `self`.
    return ((None, TESTSUITE), {})


VERDICT = run_pair(__file__, entry="test_get_source_uri_from_graph_returns_trusty",
                   calls=[trusty_nanopub])

"""Validation driver: the test signs a nanopub and checks its trusty URI.

This is an unusually strong equivalence witness: the artifact code
`RAIh8Oq-…` in the region is a cryptographic hash over the whole
nanopublication, so it only comes out right if the assertion graph built by
the island is triple-for-triple the one the original built.

The `nanopub` package is not installed in the evaluation venv; it is taken
from the corpus checkout by appending it to sys.path (appended, not
prepended, so the example's own `tests` shim package keeps priority over the
corpus one).  The region does not touch `self`, so the fixture passes None.
"""
import sys
from pathlib import Path

_CORPUS = (Path(__file__).resolve().parents[3]
           / "corpus" / "repos" / "Nanopublication__nanopub-py")
if str(_CORPUS) not in sys.path:
    sys.path.append(str(_CORPUS))

from rdfeval.harness import run_pair  # noqa: E402


def no_self():
    return ((None,), {})


VERDICT = run_pair(__file__, entry="test_nanopub_sign_uri", calls=[no_self])

"""Validation driver: the test checks that two npx:introduces triples in the
pubinfo graph make `introduces_concept` raise.

The `nanopub` package is not installed in the evaluation venv; it is taken
from the corpus checkout by appending it to sys.path.  The region does not
touch `self`, so the fixture passes None.

The assertion inside the region is what carries the RDF evidence: the
exception is raised only if the pubinfo graph really ends up holding two
distinct npx:introduces objects for the same subject.
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


VERDICT = run_pair(__file__, entry="test_introduces_concept_multiple_error",
                   calls=[no_self])

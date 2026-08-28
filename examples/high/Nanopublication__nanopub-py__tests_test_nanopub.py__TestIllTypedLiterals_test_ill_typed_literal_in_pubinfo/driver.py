"""Validation driver for Nanopublication__nanopub-py__…__test_ill_typed_literal_in_pubinfo.

The region is a pytest method that does not use ``self``, so it is called
with ``self=None``.  It is self-validating: its three assertions inspect the
literal that the region just added to ``np.pubinfo``, so a wrong term on
either side turns into an AssertionError, i.e. a non-equivalent verdict.

``nanopub`` is not installed in the eval venv; the corpus checkout is put on
sys.path (it imports as-is, its dependencies are already installed).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # nanopub_ctx shim
try:
    import nanopub  # noqa: F401
except ImportError:
    sys.path.insert(0, "/home/lefrancois/Documents/recherche/semantic_web_micropython"
                       "/github/corpus/repos/Nanopublication__nanopub-py")

from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry="test_ill_typed_literal_in_pubinfo",
                   calls=[lambda: ((None,), {})])

"""Validation driver for Nanopublication__nanopub-py__..._test_invalid_fdo_from_nanopub_network.

The region is a pytest test: it returns nothing and keeps the two graphs it
builds in locals.  Both files therefore carry an identical demo harness that
wraps MagicMock to capture those graphs and republish them at module level;
the driver compares them by isomorphism.  The test's own assertions
(is_valid is False, errors non-empty) run on both sides as well.

The region's imports are left exactly as upstream; `nanopub` is made importable
by putting the corpus checkout of the pinned commit on sys.path (see meta.json).
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
_REPO = (Path(__file__).resolve().parents[3]
         / "corpus" / "repos" / "Nanopublication__nanopub-py")
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from rdfeval.harness import run_pair  # noqa: E402

VERDICT = run_pair(__file__, entry=None, calls=None)

"""Validation driver for TestIllTypedLiterals.test_ill_typed_literal_in_assertion.

The region is a pytest test method: it returns nothing and keeps the nanopub
in a local.  Both files therefore carry an identical demo harness that wraps
the ``_minimal_valid_nanopub`` fixture helper (context shim) to capture the
instance and republish head/assertion/provenance at module level; the driver
compares them by isomorphism (pubinfo is left out: it carries a generation
timestamp).  The region's own assertions -- the ill-typed literal is reported,
and ``is_valid`` raises MalformedNanopubError mentioning it -- run on both
sides.

`nanopub` is made importable by putting the corpus checkout of the pinned
commit on sys.path (see meta.json).
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[2] / "corpus" / "repos" / "Nanopublication__nanopub-py"
for _p in (str(_HERE), str(_REPO)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from rdfeval.harness import run_pair  # noqa: E402

VERDICT = run_pair(__file__, entry=None, calls=None)

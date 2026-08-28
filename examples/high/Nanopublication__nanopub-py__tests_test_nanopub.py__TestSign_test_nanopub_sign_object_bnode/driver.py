"""Validation driver for TestSign.test_nanopub_sign_object_bnode.

The region is a pytest test method: it returns nothing and keeps the signed
nanopub in a local.  Both files therefore carry an identical demo harness that
wraps Nanopub to capture the instance and republish its four named graphs at
module level, and prints the trusty URI produced by the signature -- so the
driver compares the four graphs by isomorphism AND the signature/trusty hash
through stdout.  The region's own assertions (valid signature, no blank node
left in object position) run on both sides.

The signing profile comes from the local nanopub_context shim (the upstream
tests/conftest.py needs the online nanopub test suite); it is imported once,
so both sides sign with the same RSA key.  `nanopub` is made importable by
putting the corpus checkout of the pinned commit on sys.path (see meta.json).
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

"""Validation driver for TestCreationDefault.test_no_parameters.

The region is a pytest test method: it returns nothing and keeps the nanopub
in a local.  Both files therefore carry an identical demo harness that wraps
Nanopub to capture the instance and republish head/assertion/provenance at
module level; the driver compares them by isomorphism (pubinfo is left out:
it carries a generation timestamp).  The region's own assertions
(source_uri is None, head non-empty, exactly one np:Nanopublication /
np:hasProvenance / np:hasPublicationInfo triple) run on both sides.

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

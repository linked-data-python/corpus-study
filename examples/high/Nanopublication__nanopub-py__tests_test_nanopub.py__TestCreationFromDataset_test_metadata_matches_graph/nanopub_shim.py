# Context shim (see meta.json): the region comes from tests/test_nanopub.py of
# Nanopublication/nanopub-py@05022dc4bc, which is not an installed package in
# the evaluation environment.  Importing this module puts the corpus checkout
# on sys.path so that ``import nanopub`` resolves to exactly that commit.
# Imported identically by original.py and translated.ldpy.
import sys
from pathlib import Path

_CHECKOUT = (Path(__file__).resolve().parents[3]
             / "corpus" / "repos" / "Nanopublication__nanopub-py")
if str(_CHECKOUT) not in sys.path:
    sys.path.insert(0, str(_CHECKOUT))

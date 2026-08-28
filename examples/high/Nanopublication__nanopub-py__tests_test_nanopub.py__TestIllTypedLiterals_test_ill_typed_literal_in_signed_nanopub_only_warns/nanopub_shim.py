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


# Helper used by the region, copied verbatim from tests/test_nanopub.py
# (lines 763-773) of the same commit.  It is *context*, not part of the
# extracted region, so it stays Python on both sides.
from typing import Optional  # noqa: E402

from rdflib import DC, PROV, Literal, URIRef  # noqa: E402

from nanopub import Nanopub, NanopubConf, namespaces  # noqa: E402


def _minimal_valid_nanopub(conf: Optional[NanopubConf] = None) -> Nanopub:
    """A nanopub with the bare minimum needed to pass ``is_valid``."""
    np = Nanopub(conf=conf if conf is not None else NanopubConf())
    np.assertion.add(
        (URIRef("http://test"), namespaces.HYCL.claims, Literal("test claim"))
    )
    np.provenance.add(
        (np.assertion.identifier, PROV.wasAttributedTo, URIRef("http://someone"))
    )
    np.pubinfo.add((np._metadata.namespace[""], DC.creator, Literal("tester")))
    return np

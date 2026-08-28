# Context shim (see meta.json): `_minimal_valid_nanopub` is a module-level
# helper of tests/test_nanopub.py in Nanopublication/nanopub-py@05022dc4bc
# (lines 763-773) that the extracted region calls but that the extractor did
# not carry over.  It is copied verbatim below; the only addition is the
# `_CREATED` bookkeeping, which lets the demo harness at the end of
# original.py / translated.ldpy expose the assertion graph the region fills.
# Used identically by original.py and translated.ldpy.
from typing import Optional

from rdflib import DC, PROV, Literal, URIRef

from nanopub import Nanopub, NanopubConf, namespaces

_CREATED: list = []


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
    _CREATED.append(np)
    return np


def last_nanopub() -> Nanopub:
    """The most recently built nanopub (demo harness only)."""
    return _CREATED[-1]

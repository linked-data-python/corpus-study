# Context shim (see meta.json): _minimal_valid_nanopub, the fixture helper the
# region calls, copied verbatim from tests/test_nanopub.py (lines 763-773) of
# Nanopublication/nanopub-py@05022dc4bc, with the imports it needs.  It lives
# in the same test module as the region upstream; here it is a local module so
# the extracted region can run on its own.
# Imported IDENTICALLY by original.py and translated.ldpy.
from typing import Optional

from rdflib import DC, PROV, Literal, URIRef

from nanopub import Nanopub, NanopubConf, namespaces


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

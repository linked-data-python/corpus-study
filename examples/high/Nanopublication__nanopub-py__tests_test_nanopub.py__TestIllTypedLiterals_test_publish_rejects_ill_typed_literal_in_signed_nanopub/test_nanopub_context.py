# Context shim (see meta.json): _minimal_valid_nanopub, the helper defined
# next to the region in tests/test_nanopub.py at
# Nanopublication/nanopub-py@05022dc4bc (lines 763-773, verbatim).  The
# extraction kept only the region, so the helper it calls has to be
# re-supplied.  Used IDENTICALLY by original.py and translated.ldpy.
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

"""Context shim: the fixture helper the extracted test method calls.

Copied verbatim from Nanopublication/nanopub-py@05022dc4bc
``tests/test_nanopub.py`` lines 763-773 (a module-level helper of the test
module the region was extracted from), with the imports it needs.
``original.py`` and ``translated.ldpy`` import this shim identically; only the
extracted region differs between them.
"""
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

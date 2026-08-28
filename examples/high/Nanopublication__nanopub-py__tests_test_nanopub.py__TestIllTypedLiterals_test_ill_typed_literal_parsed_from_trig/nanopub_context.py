"""Context shim for the Nanopublication/nanopub-py region.

Two things the extracted region needs and cannot get on its own:

1. the ``nanopub`` package itself, which is not installed in the
   evaluation venv but imports cleanly from the corpus checkout (all of
   its runtime dependencies -- rdflib, requests, typer, yatiml,
   pycryptodome, SPARQLWrapper, pyshacl -- are installed); importing this
   module puts that checkout on ``sys.path``;

2. ``_minimal_valid_nanopub``, a helper defined a few lines above the
   region in the same test module and therefore having no import line of
   its own.  It is copied VERBATIM from
   Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py:763-773.

This module is imported IDENTICALLY by original.py and translated.ldpy.
"""

import sys
from typing import Optional

_CHECKOUT = ("/home/lefrancois/Documents/recherche/semantic_web_micropython"
             "/github/corpus/repos/Nanopublication__nanopub-py")
if _CHECKOUT not in sys.path:
    sys.path.insert(0, _CHECKOUT)

from rdflib import DC, Literal, PROV, URIRef  # noqa: E402

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

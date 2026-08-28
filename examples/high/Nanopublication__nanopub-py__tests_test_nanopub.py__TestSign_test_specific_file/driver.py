"""Validation driver for TestSign.test_specific_file.

The region is a pytest test method: it returns nothing and keeps the signed
nanopub in a local.  Both files therefore carry an identical demo harness that
subclasses Nanopub to snapshot the four named graphs immediately before
sign(), and republishes them at module level; the driver compares them by
isomorphism.

The signed result itself is NOT compared, and cannot be: the JSON-LD file's
many blank nodes get fresh random identifiers at every parse, and nanopub's
_replace_blank_nodes() turns them into ...#_1, ...#_2 URIs numbered in store
iteration order.  Two runs of one and the same original.py already produce
different trusty URIs (checked), so the signature is not a usable oracle here.

One more thing is made reproducible in the DRIVER (never in either
representation, so neither side is favoured):

the region turns BOTH generated-time options on, so pubinfo/provenance would
carry a `prov:generatedAtTime` differing between the two executions;
`nanopub.nanopub.datetime` is therefore frozen for the whole comparison.

The region also opens "./tests/resources/many_bnodes_with_annotations.json"
relative to the working directory, so the driver chdir's to the example
directory, where that file has been copied (5 KB, Apache-2.0 repository,
snippet_ok).

The signing profile comes from the local nanopub_context shim (the upstream
tests/conftest.py needs the online nanopub test suite); it is imported once,
so both sides sign with the same RSA key.  `nanopub` is made importable by
putting the corpus checkout of the pinned commit on sys.path (see meta.json).
"""
import datetime as _datetime
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True
_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[2] / "corpus" / "repos" / "Nanopublication__nanopub-py"
for _p in (str(_HERE), str(_REPO)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
os.chdir(_HERE)


class _FrozenDatetime(_datetime.datetime):
    """A clock that does not move between the two executions."""

    @classmethod
    def now(cls, tz=None):
        return cls(2026, 8, 28, 12, 0, 0, tzinfo=_datetime.timezone.utc)


import nanopub.nanopub as _nanopub_module  # noqa: E402

_nanopub_module.datetime = _FrozenDatetime

from rdfeval.harness import run_pair  # noqa: E402

VERDICT = run_pair(__file__, entry=None, calls=None)

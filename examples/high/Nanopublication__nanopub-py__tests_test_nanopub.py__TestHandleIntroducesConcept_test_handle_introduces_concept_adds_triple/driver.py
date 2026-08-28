"""Validation driver: the region is a unit test of Nanopub's
_handle_introduces_concept.

It is a method, but ``self`` is never used, so the fixture passes None for it.
The region returns nothing; its observable behaviour is the assertion that the
pubinfo graph is non-empty after the call, which both sides must reach without
raising.  (The pubinfo graph itself carries a prov:generatedAtTime stamped at
call time, so it could not be compared across the two runs anyway.)

Note that translated.ldpy is byte-identical to original.py below the header:
the region contains no construct the notation can express (see meta.json).
"""
from rdfeval.harness import run_pair


def unused_self():
    return ((None,), {})


VERDICT = run_pair(__file__, entry="test_handle_introduces_concept_adds_triple",
                   calls=[unused_self])

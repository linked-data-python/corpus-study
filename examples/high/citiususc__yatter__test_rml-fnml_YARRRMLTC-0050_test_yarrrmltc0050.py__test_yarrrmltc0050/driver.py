"""Validation driver for citiususc__yatter ... test_yarrrmltc0050.

The region is a pytest test taking no argument and returning nothing, so an
entry-based run would compare None against None.  Both sides therefore carry
an identical demo-harness section (see meta.json) that calls the test -- its
own `assert compare.isomorphic(...)` still fires -- and re-exposes the two
graphs it builds internally, so entry=None compares them by isomorphism plus
the captured stdout.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)

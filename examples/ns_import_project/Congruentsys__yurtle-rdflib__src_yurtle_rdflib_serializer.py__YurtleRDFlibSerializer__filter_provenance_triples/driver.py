"""Validation driver for Congruentsys__yurtle-rdflib__src_yurtle_rdflib_serializer.py__YurtleRDFlibSerializer__filter_provenance_triples.

`demo()` (identical on both sides, appended after the extracted region --
see meta.json) builds a minimal fake `self` (a `.store` graph) and calls
`_filter_provenance_triples(self)`, returning the filtered graph -- the
region's only observable effect (isomorphism-compared by the harness).
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[((), {})],
)

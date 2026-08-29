"""Validation driver for DataDrivenCPS__acquirium__src_acquirium_internals_qudt_units.py__QUDTUnitConverter__search_label_contains.

This region READS a graph, so the oracle is the equality of the values both
versions produce from the same input graph (design record corpus/405), not
isomorphism.  `demo(text)` (identical on both sides, appended after the
extracted region -- see meta.json) builds a fresh `qudt_context.ConverterStub`
from fixture.ttl and calls `_search_label_contains(stub, text)`, returning
what the region itself returns.

Three calls exercise: (1) a match reached only after skipping a
same-predicate, same-substring candidate that fails `_looks_like_unit`
(fixture.ttl's ex:galacticSurvey); (2) the zero-solution case; (3) a match
reached only through a LATER predicate in the priority list (ucumCode).
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='demo',
    fixture="fixture.ttl",  # informational here: demo() loads it itself, see above
    calls=[(("gal",), {}), (("doesnotexist",), {}), (("min",), {})],
)

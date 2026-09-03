"""Validation driver for eliozo__worksheet-generation-with-llms__scripts_rdfgen_csv_to_concepts.py__addToRdfGraph.

`addToRdfGraph(g, conceptID, termLV, descLV, termEN=None)` mutates `g` in
place and returns nothing, so the driver compares the `g` argument itself
(isomorphism) after the call. Each call is a lambda factory, invoked once
per side, so the two sides never mutate the same Graph() instance (see
rdfeval.harness.run_pair's own note on mutable arguments).

CALL_1 -- termEN=None: exercises the `if not termEN: termEN = conceptID...`
fallback branch, and a hyphenated conceptID ("foo-bar") through the
`eliozo:{"TRM-" + conceptID}` computed prefixed name -- plain string
concatenation, not percent-encoding, matching original.py's own
`eliozo_ns + "TRM-" + conceptID` exactly (see meta.json). descLV is a real
value: exercises the descLV triple.

CALL_2 -- termEN given explicitly, descLV="": the empty-string branch of
`if descLV and descLV != "" and descLV != "NA":` -- no descLV triple.

CALL_3 -- descLV="NA": the third guard of the same condition -- no descLV
triple either, with a different conceptID/termLV/termEN combination so the
run is not just CALL_2 with one field swapped.
"""
from rdflib import Graph

from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='addToRdfGraph',
    calls=[
        lambda: ((Graph(), "foo-bar", "kāds termins", "kāds apraksts"), {}),
        lambda: ((Graph(), "baz", "cits vārds", ""), {"termEN": "Explicit EN"}),
        lambda: ((Graph(), "qux", "trešais vārds", "NA"), {"termEN": "Another EN"}),
    ],
)

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

Repair 2026-10-30: demo() takes the fixture as a second parameter (a seam in
the harness part, identical on both sides), and the calls below add:
  fixture_predicates.ttl - each tracked predicate decides one call
      ("MÈTRE": skos:prefLabel, language-tagged, casefold; "symtok":
      qudt:symbol, typed literal, an IRI object holding the same token
      skipped by the Literal guard, and alone to hold "symtok-iri", which
      must give None; "0": qudt:uneceCommonCode on the integer
      zero); "commtok" sits only under rdfs:comment on a real unit and must
      give None (kills a predicate widened to a variable); "both" is under
      rdfs:label and qudt:symbol on two units, the label wins (predicate
      order); "skiptok" is held by a non-unit only (None); "STRASSE" checks
      casefold against "Straße"; "" matches the first literal under the
      first predicate that belongs to a unit;
  fixture.ttl with ""       - the empty search on the first fixture;
  fixture_empty.ttl         - zero triples, for "" and for a real token.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='demo',
    fixture="fixture.ttl",  # informational here: demo() loads it itself, see above
    calls=[(("gal",), {}), (("doesnotexist",), {}), (("min",), {}),
           (("commtok", "fixture_predicates.ttl"), {}),
           (("MÈTRE", "fixture_predicates.ttl"), {}),
           (("symtok", "fixture_predicates.ttl"), {}),
           (("symtok-iri", "fixture_predicates.ttl"), {}),
           (("0", "fixture_predicates.ttl"), {}),
           (("both", "fixture_predicates.ttl"), {}),
           (("skiptok", "fixture_predicates.ttl"), {}),
           (("STRASSE", "fixture_predicates.ttl"), {}),
           (("", "fixture_predicates.ttl"), {}),
           (("",), {}),
           (("", "fixture_empty.ttl"), {}),
           (("gal", "fixture_empty.ttl"), {})],
)

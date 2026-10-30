"""Validation driver for kumagallium__asterism__ingest_tests_test_papers_dataset.py__test_structure_round_trip.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405). `test_structure_round_trip()` takes no argument -- it builds its
own graph from `_seed_ttl()` (redefined in original.py/translated.ldpy to
read a fixture of this directory, see their header comments) -- so the
harness's automatic fixture= injection (which passes a parsed graph as the
entry point's first argument) does not apply here.

`test_structure_round_trip` only ever asserts and returns None; `demo()`
(added identically to both representations) turns a failed assertion into a
comparable value -- "ok" or ("assertion-failed", message) -- and its
`fixture` parameter chooses the graph `_seed_ttl()` reads. The region body
is untouched.

A test that only asserts sees one graph; on fixture.ttl alone, both
interpolations ({rdflib.URIRef(PAPER)}, {rdflib.URIRef(sent)}) and every
type pattern could be widened without changing "ok" (triage of 2026-10-27).
Each extra call below makes ONE pattern decisive: the original fails at a
known assertion, and widening that pattern (a bound term made a variable,
a pattern dropped) moves the outcome to "ok" or to another assertion,
whatever order the store yields solutions in:

  fixture.ttl                      two complete chains, neighbours -> "ok"
  fixture_other_paper_only.ttl     zero solutions for PAPER; only another
                                   paper has a chain ({URIRef(PAPER)})
  fixture_untyped_sec/para/sent    the chain's sec/para/sent carries another
                                   type (the three 'a doco:X' patterns)
  fixture_paper/para/sent_other_predicate
                                   one po:contains link of the 'down' path
                                   is another predicate
  fixture_uplinks_elsewhere.ttl    the sentence has no up-link, another
                                   sentence has both ({URIRef(sent)}, both
                                   occurrences and each one)
  fixture_no_quoted.ttl            no prov:wasQuotedFrom on the sentence
  fixture_no_context.ttl           no nif:referenceContext on the sentence
  fixture_wrong_context.ttl        the last assertion fails (ctx differs)
  fixture_decoys_first.ttl         neighbours written before the real chain,
                                   for the 'up' patterns that only an order
                                   can expose (LIMIT 1 without ORDER BY)
"""
from rdfeval.harness import run_pair

FIXTURES = [
    "fixture.ttl",
    "fixture_other_paper_only.ttl",
    "fixture_untyped_sec.ttl",
    "fixture_untyped_para.ttl",
    "fixture_untyped_sent.ttl",
    "fixture_paper_other_predicate.ttl",
    "fixture_para_other_predicate.ttl",
    "fixture_sent_other_predicate.ttl",
    "fixture_uplinks_elsewhere.ttl",
    "fixture_no_quoted.ttl",
    "fixture_no_context.ttl",
    "fixture_wrong_context.ttl",
    "fixture_decoys_first.ttl",
]

VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[(lambda f=f: ((), {"fixture": f})) for f in FIXTURES],
)

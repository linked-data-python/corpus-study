"""Validation driver for kumagallium__asterism__ingest_tests_test_papers_dataset.py__test_structure_round_trip.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405). `test_structure_round_trip()` takes no argument -- it builds its
own graph from `_seed_ttl()` (redefined in original.py/translated.ldpy to
read `fixture.ttl`, this directory, see their header comments) -- so the
harness's automatic fixture= injection (which passes a parsed graph as the
entry point's first argument) does not apply here; `fixture.ttl` still is
the reading oracle's input, just reached a different way.

`test_structure_round_trip` only ever asserts and returns None; `demo()`
(added identically to both representations) turns a failed assertion into a
comparable value instead of letting run_pair abort on the first raise, the
same convention already used by
examples/trav_single_value/BD2KOnFHIR__fhirtordf__.../test_value.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[lambda: ((), {})],
)

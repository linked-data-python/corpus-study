"""Validation driver for Blackcat-Informatics__purrdf__bindings_python_tests_rdflib_suite_vendor_test_agg_undef.py__template_tst.

IDENTITY translation (see meta.json): `agg_func` is the SPARQL AGGREGATE
FUNCTION NAME (SUM, MIN, MAX, SAMPLE, COUNT, GROUP_CONCAT), spliced with
`%s` into `SELECT ?x (%s(?y_) as ?y) { ... }` -- a syntax position, not a
term, so `s{ }`'s term-position interpolation cannot carry it (see
translation_notes for the argument).

`template_tst` only asserts and prints; it takes no graph argument to
mutate and returns nothing, so what proves the (unmodified) region still
computes right is the six real invocations from upstream's own
`get_aggregates_tests()` (AVG is commented out there too, at the pinned
commit) -- see `call[i].result`/stdout captured by run_pair.

No external graph is read: `g = Graph()` is built empty *inside* the
function, and all data comes from the query's own VALUES clause -- so
there is nothing for `fixture.ttl` to hold (see that file).
"""
from rdflib import Literal

from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='template_tst',
    calls=[
        (("SUM", Literal(0), Literal(42)), {}),
        (("MIN", None, Literal(42)), {}),
        (("MAX", None, Literal(42)), {}),
        (("SAMPLE", None, Literal(42)), {}),
        (("COUNT", Literal(0), Literal(1)), {}),
        (("GROUP_CONCAT", Literal(""), Literal("42")), {}),
    ],
)

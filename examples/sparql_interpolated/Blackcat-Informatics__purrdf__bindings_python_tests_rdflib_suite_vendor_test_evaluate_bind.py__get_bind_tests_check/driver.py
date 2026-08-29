"""Validation driver for Blackcat-Informatics__purrdf__bindings_python_tests_rdflib_suite_vendor_test_evaluate_bind.py__get_bind_tests_check.

Establishes semantic equivalence of original.py and translated.ldpy -- here
an IDENTITY translation (see meta.json): `expr` is a whole SPARQL clause
(a `bind(...)` of varying shape) spliced into the query text with `%s`, not
a term, so `s{ }`'s term-position interpolation cannot carry it. See
translation_notes for the argument.

`check(expr, var, obj)` only asserts; it returns nothing to compare, so the
three real invocations from get_bind_tests() (upstream, at the pinned
commit) are what proves the (unmodified) region still computes right against
the restored `g`.
"""
from rdflib import Literal, URIRef

from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='check',
    calls=[
        (('bind("thing" as ?name)', "name", Literal("thing")), {}),
        (('bind(<http://example.org/other> as ?other)', "other",
          URIRef("http://example.org/other")), {}),
        (('bind(:Thing as ?type)', "type",
          URIRef("http://example.org/ns#Thing")), {}),
    ],
)

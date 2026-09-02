"""Validation driver for BD2KOnFHIR__fhirtordf__fhirtordf_rdfsupport_fhirgraphutils.py__code.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

`code(g, subject, predicate, system=None, asLiteral=False)` takes `subject`
and `predicate` as external arguments, so a bare `fixture=` (which calls the
entry point with the parsed graph as its sole argument) is not enough: each
call below parses its own fixture graph and resolves `subject`/`predicate`
as plain named IRIs (no BNode lookup needed here, unlike the blathers
example -- ex:Obs1/ex:Obs2/ex:Obs3/ex:hasCode are all fixed IRIs).

Four calls exercise the stratum (trav_single_value, `g.value` -> `m{ }.first()`):
  * match_no_system   -- ex:Obs1 has exactly one coding, so `system=None`
                          returns its code without any iteration-order
                          dependency.
  * match_by_system   -- ex:Obs2 has two codings; only one matches the given
                          system, so the result does not depend on order.
  * zero_value        -- ex:Obs3 carries no ex:hasCode triple at all: the
                          ZERO-solution case where g.value()/m{ }.first()
                          both answer None, and code() returns None before
                          ever reaching the coding loop.
  * match_as_literal  -- same as match_no_system but asLiteral=True, so the
                          inner value() helper returns a Literal, not a str.
None of the calls ever reaches ex:Obs4's coding (the neighbourhood).
"""
from rdflib import Namespace

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = "fixture.ttl"
EX = Namespace("http://example.org/")


def match_no_system():
    g = fixture_graph(FIXTURE)
    return ((g, EX.Obs1, EX.hasCode), {})


def match_by_system():
    g = fixture_graph(FIXTURE)
    return ((g, EX.Obs2, EX.hasCode), {"system": "sys-y"})


def zero_value():
    g = fixture_graph(FIXTURE)
    return ((g, EX.Obs3, EX.hasCode), {})


def match_as_literal():
    g = fixture_graph(FIXTURE)
    return ((g, EX.Obs1, EX.hasCode), {"asLiteral": True})


VERDICT = run_pair(
    __file__,
    entry='code',
    fixture=FIXTURE,
    calls=[match_no_system, match_by_system, zero_value, match_as_literal],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets. Not
    # needed here: each call's result does not depend on iteration order
    # (see fixture.ttl / docstring above).
)

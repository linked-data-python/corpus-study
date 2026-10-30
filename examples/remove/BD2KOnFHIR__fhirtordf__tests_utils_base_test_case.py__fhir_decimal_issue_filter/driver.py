"""Validation driver for BD2KOnFHIR__fhirtordf__tests_utils_base_test_case.py__fhir_decimal_issue_filter.

This region READS a graph, so the oracle is not isomorphism of a graph the
region builds but the equality of what the two versions produce from the same
input (design record corpus/405).  It reads and mutates THREE graphs, so the
reading oracle needs two Turtle inputs, parsed fresh for each side:
`fixture.ttl` is in_first, `fixture_second.ttl` is in_second, and in_both
starts empty.  The function returns None: what is compared is the three graphs
it leaves behind (arguments 0, 1 and 2, by RDF isomorphism).

The fixtures are part of the translation: several solutions of the pattern
(three decimal pairs the filter must move), the zero-solution case
(in_second has no value for ex:obs4, so `.value()`/`.first()` answer None),
and neighbours that must not match — another datatype, a plain literal, a
URIRef object, decimals whose values differ, and triples in in_second with no
counterpart at all.

The `-{ }` / `+{ }` islands bind s, p, o fully, so what the fixtures must also
tell apart is a removal whose bound term was widened to a wildcard.  Each term
therefore has a neighbour that shares it with a moved triple without being that
triple: same subject and object but another predicate (obs1 ex:alt), same
predicate and object but another subject (obs10 in in_first, obs11 in
in_second), same subject and predicate but another object (obs14 in in_first,
obs15 with two equal decimals in in_second, obs2 ex:alt on the in_second side).
A decimal facing an integer of equal numeric value (obs12, obs13; Decimal(2) ==
2) is what makes the two datatype tests observable.  Run against the translation
with each of these changed in a copy, the check fails: object widened on the
in_first or in_second removal, predicate widened on either, subject widened on
either, the datatype test on `o` dropped, the datatype test on `o_2` dropped.
"""
from rdflib import Graph

from rdfeval.harness import fixture_graph, run_pair

FIRST = "fixture.ttl"
SECOND = "fixture_second.ttl"


def three_graphs():
    return ((Graph(), fixture_graph(FIRST), fixture_graph(SECOND)), {})


VERDICT = run_pair(
    __file__,
    entry='fhir_decimal_issue_filter',
    fixture=FIRST,
    calls=[three_graphs],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)

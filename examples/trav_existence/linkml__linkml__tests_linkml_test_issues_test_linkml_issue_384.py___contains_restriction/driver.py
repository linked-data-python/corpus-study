"""Validation driver for linkml__linkml__tests_linkml_test_issues_test_linkml_issue_384.py___contains_restriction.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405). `fixture.ttl` is parsed fresh for each side.

The entry point takes five arguments (g, c, prop, pred, filler), not just a
graph, so run_pair's default single-argument call ("pass the fixture graph
as the sole argument") does not apply here: `calls` supplies the extra IRIs
explicitly, matching what fixture.ttl declares.

Four cases:
  * (C1, p1, someValuesFrom, F1) -> True: the first restriction on C1
    matches all three joined patterns (several solutions of the head
    pattern -- C1 has two restrictions -- collapse correctly to one exists).
  * (C1, p2, someValuesFrom, F9) -> False: p2's restriction on C1 exists but
    its filler is F2, not F9 -- exercises the join failing on the last
    triple.
  * (C2, p1, someValuesFrom, F1) -> False / zero solution: C2's only
    restriction uses p1 but fillers F9, not F1.
  * (C1, p1, someValuesFrom, F1) against the PlainSuperclass neighbour is
    implicit: PlainSuperclass has no owl:onProperty at all, so it can never
    satisfy the join even though it IS a subClassOf of C1 -- proven by case
    1 succeeding only via R1/R2, never via PlainSuperclass.
"""
from pathlib import Path

from rdflib import Namespace

from rdfeval.harness import run_pair, fixture_graph

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
EX = Namespace("http://example.org/")


def _case(c, prop, pred, filler):
    def make():
        g = fixture_graph(FIXTURE)
        return (g, EX[c], EX[prop], pred, EX[filler]), {}
    return make


VERDICT = run_pair(
    __file__,
    entry="_contains_restriction",
    fixture="fixture.ttl",
    calls=[
        _case("C1", "p1", Namespace("http://www.w3.org/2002/07/owl#").someValuesFrom, "F1"),
        _case("C1", "p2", Namespace("http://www.w3.org/2002/07/owl#").someValuesFrom, "F9"),
        _case("C2", "p1", Namespace("http://www.w3.org/2002/07/owl#").someValuesFrom, "F1"),
    ],
)

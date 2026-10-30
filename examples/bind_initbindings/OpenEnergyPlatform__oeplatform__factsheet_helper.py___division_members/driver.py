"""Validation driver for OpenEnergyPlatform__oeplatform__factsheet_helper.py___division_members.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

`_division_members(g, division)` takes TWO arguments, so the default
"single graph argument" call the harness builds from `fixture=` alone does
not fit; `calls=` supplies `(fixture_graph(...), division)` explicitly for
three divisions: one with matches (`ex:division1`, covering all three UNION
branches, the self-reference the FILTER drops, and the blank node the
`isinstance` check drops -- see fixture.ttl), one with none
(`ex:divisionZero`, the zero-solution case) and `ex:division2`, which has
members of its own through each branch (so the bound division of every branch,
and not only the first, decides the result).

The fixture also holds, for branches 2 and 3 alike, neighbours that share the
other terms and differ in one: wrong owl:onProperty, restriction not typed
owl:Restriction, wrong filler (someValuesFrom another division, or
owl:allValuesFrom), plus a lowercase label and an unlabelled member to pin the
sort key (`.lower()`, fallback to the IRI).  The mutants run against it are
listed in meta.json ("repair").

`ordered=True`: unlike a bare query result, this region's OWN return value is
`sorted(members, key=...)` -- it imposes an order, so the harness must not
discard it as multiset noise. The fixture's labels are pairwise distinct so
the sort order is unambiguous regardless of set-iteration order.
"""
from pathlib import Path

from rdflib import Namespace

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
EX = Namespace("http://example.org/")


def _call(division):
    def _make():
        return (fixture_graph(FIXTURE), division), {}
    return _make


VERDICT = run_pair(
    __file__,
    entry='_division_members',
    fixture="fixture.ttl",
    ordered=True,
    calls=[
        _call(EX.division1),     # three solutions, after the FILTER/isinstance drops
        _call(EX.divisionZero),  # zero solutions
        _call(EX.division2),     # members through branches 1 to 3, none of division1's
    ],
)

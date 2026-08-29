"""Validation driver for TheWorldAvatar__mcp-tool-layer__scripts_output_conversion_ttl_to_json_step_step_details.py__query_step_details_all_fields.

This region READS a graph (two SELECTs, both `initBindings={"S": ...}`), so
the oracle is not isomorphism but the equality of the values both versions
produce from the same input graph (design record corpus/405).  `fixture.ttl`
is parsed fresh for each side (`fixture_graph`, once per call so neither
side's read can leak into the other's).

Two calls: `ex:step1`, whose properties exercise the list-merge branch (two
`ex:hasReagent` values), the plain-literal branch (`ex:hasDuration`), the
prefer-the-label branch (`ex:reagentA`/`ex:reagentB` both carry
`rdfs:label`), and its own `rdfs:label` (the second query); and `ex:step2`,
which owns only its own `rdf:type` triple -- `FILTER(?p != rdf:type)` empties
the first query and it has no `rdfs:label` of its own, so BOTH queries the
region issues return zero rows for it (the zero-solution case). `ex:other_step`
in the fixture carries the same predicates as `ex:step1` under a different
subject and must not leak into either step's results.
"""
from pathlib import Path

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"


def call(step_uri):
    def _make():
        return (fixture_graph(FIXTURE), step_uri), {}
    return _make


VERDICT = run_pair(
    __file__,
    entry='query_step_details_all_fields',
    fixture="fixture.ttl",
    calls=[
        call("http://example.org/step1"),
        call("http://example.org/step2"),
    ],
)

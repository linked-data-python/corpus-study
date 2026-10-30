"""Validation driver for ksahlmann__myno__myno-agriculture_virtual-device_aggregatPreload.py__get_event_functions.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

The region returns the rdflib Result (materialised and compared as a
multiset of rows), prints each row and the JSON serialisation (stdout is
compared too).  Two calls:

  call[0]  fixture.ttl — several solutions; a DUPLICATE row (two devices
           share func1: the query has no DISTINCT, so the row must appear
           twice); neighbours that must not match, one per pattern of the
           join: a functionality of another type, an EventFunctionality no
           service exposes, one exposed but held by no device (kills a
           dropped ?device pattern), a data point without mqttTopic, a
           service linked by hasInputDataPoint, and a data point with an
           extra predicate (kills base:mqttTopic widened to ?p);
  call[1]  an empty graph — the zero-solution case: no row printed, an
           empty JSON result, an empty Result returned.

The caller in the repository (aggregatPreload.py:195-208) passes a plain
rdflib Graph filled by a JSON-LD parse, which is what both calls pass.
"""
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import fixture_graph, run_pair

_FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"

VERDICT = run_pair(
    __file__,
    entry='get_event_functions',
    fixture="fixture.ttl",
    calls=[
        lambda: ((fixture_graph(_FIXTURE),), {}),
        lambda: ((Graph(),), {}),
    ],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)

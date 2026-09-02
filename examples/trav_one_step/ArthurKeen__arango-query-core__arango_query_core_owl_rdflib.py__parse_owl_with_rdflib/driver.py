"""Validation driver for ArthurKeen__arango-query-core__arango_query_core_owl_rdflib.py__parse_owl_with_rdflib.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405). The region's own signature takes the *raw Turtle text* as a
string (`turtle_text: str`) and parses it itself -- so `fixture.ttl`'s
content is read as TEXT and passed as that argument, not parsed into a
Graph object beforehand (the default `fixture=` behaviour of `run_pair`
hands the entry point a pre-parsed Graph, which does not fit this
signature; hence the explicit `calls=`).

See fixture.ttl for what it covers per read site.

The returned MappingBundle is compared with `ordered=False` (the default
for a fixture run): its `conceptual_schema`/`physical_mapping` dicts hold
lists (`entities`, `relationships`) built by iterating subject sets no
store promises an order for.
"""
from pathlib import Path

from rdfeval.harness import run_pair

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"


def call_default():
    return ((FIXTURE.read_text(),), {})


VERDICT = run_pair(
    __file__,
    entry='parse_owl_with_rdflib',
    fixture="fixture.ttl",
    calls=[call_default],
)

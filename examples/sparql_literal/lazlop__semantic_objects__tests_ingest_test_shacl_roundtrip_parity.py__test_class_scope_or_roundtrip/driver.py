"""Validation driver for lazlop__semantic_objects__tests_ingest_test_shacl_roundtrip_parity.py__test_class_scope_or_roundtrip.

Establishes semantic equivalence of original.py and translated.ldpy.

This region reads a graph (two SPARQL queries, an ASK and a SELECT), so the
oracle is the values both versions produce, not isomorphism (design record
corpus/405). There is no fixture.ttl: `test_class_scope_or_roundtrip` takes
no argument and builds its own graph via `_shacl_graph()`, so the input
graph lives in `_context.py` (see meta.json for why) rather than in a Turtle
file passed through `fixture=`. `calls=[((), {})]` calls the entry point
with no arguments, once per side.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='test_class_scope_or_roundtrip',
    calls=[((), {})],
)

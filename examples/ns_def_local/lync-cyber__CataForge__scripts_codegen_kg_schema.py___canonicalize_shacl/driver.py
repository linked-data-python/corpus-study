"""Validation driver for lync-cyber__CataForge__scripts_codegen_kg_schema.py___canonicalize_shacl.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  The region's entry point takes Turtle TEXT (it parses its own
graph internally), not a Graph object, so the fixture is read as text and
passed directly rather than through `fixture=` (which would hand it a
pre-parsed Graph).

`fixture.ttl` holds several solutions of the pattern the region reads
(`sh:order`, `sh:ignoredProperties`, `sh:in`), a subject with none of them
(the zero-solution case), and neighbouring predicates that must NOT be
touched.
"""
from pathlib import Path

from rdfeval.harness import run_pair

_FIXTURE = Path(__file__).parent / "fixture.ttl"

VERDICT = run_pair(
    __file__,
    entry='_canonicalize_shacl',
    calls=[lambda: ((_FIXTURE.read_text(),), {})],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets. The
    # returned string is itself already sorted N-Triples, so string equality
    # (the default comparison) is exact either way.
)

"""Validation driver for TheWorldAvatar__mcp-tool-layer__scripts_output_conversion_ttl_to_json_ontosynthesis_cbu_conversion.py__build_cbu_json_from_graph.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405). `fixture.ttl` is parsed fresh for each side; see that file's own
header for what each of its five MOPs exercises (several solutions of every
joined pattern, several zero-solution branches, and neighbouring triples that
must not match).

`entry` is `run(graph)`, a one-line wrapper both files carry identically
(see meta.json): the region itself is a bare `for` statement extracted from
inside build_cbu_json_from_graph (kind: statement, not a function), so `run`
gives it a callable shape and returns `procedures`, the list the region
builds. Solution order (which MOP, which CBU, is visited first) is not part
of this region's meaning -- default `ordered=False` for a fixture run.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry="run",
    fixture="fixture.ttl",
)

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

fixture.ttl was extended by the repair of 2026-10-30 (triage:
equivalence-doubt); see its last section. It adds MOPs whose CCDC literal is
falsy in Python ("" and 0: the original tests the list of values, so both
must still produce an entry), a MOP with two CCDC numbers (first value
kept, no exception), and neighbours sharing two of the three terms of a
pattern -- a non-MOP pointing at the MOP class through another predicate,
an orphan CBU with its own owl:sameAs, extra properties (one an IRI with a
label) on a real CBU and a real chemical input -- so that widening any
bound term of the region's patterns into a variable changes the result.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry="run",
    fixture="fixture.ttl",
)

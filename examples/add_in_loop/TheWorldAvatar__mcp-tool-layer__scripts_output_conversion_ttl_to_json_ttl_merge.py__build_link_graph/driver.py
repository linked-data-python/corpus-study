"""Validation driver for TheWorldAvatar__mcp-tool-layer__scripts_output_conversion_ttl_to_json_ttl_merge.py__build_link_graph.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

The fixture is part of the translation: it must hold several solutions of the
pattern the region reads, the zero-solution case, and neighbouring triples
that must NOT match.

Fixture additions that make each guard of the region matter (each one was
checked by replacing the guard in a copy of translated.ldpy and running
`rdfeval check`; every replacement below is rejected):
  * `ex:species1` carries a second type `ex:ExtraType` that is not allowed:
    `if t in allowed_types:` -> `if True:`.
  * `ex:species1 ex:note ex:unselected1`: selected subject, unselected object,
    so `s in selected and o in selected` -> `s in selected` / `or`; with
    `ex:other1 ex:relatedTo ex:species1` (already there) the `o in selected`
    only variant is rejected too.
  * `ex:species1 ontosyn:hasChemicalInput ex:input1`: a selected node that is
    not a ChemicalSynthesis, so the synthesis filter -> `if True` is rejected.
  * `ex:synth4` has two more inputs, `ex:input2` (no type, no label) and
    `ex:input3` (label only): `(chem_input, rdf:type, ChemicalInput) in g`
    -> `True` and -> `False` are both rejected, and so are the removals of the
    label island and of the hasChemicalInput island.
  * `ex:synth5` bridges to the selected `ex:species1`, which is not a MOP:
    dropping `(mop, rdf:type, MOP) in g` (keeping `mop in selected`) is rejected.
  * `ex:synth6` reaches `ex:mop1` (also reached by `ex:synth1`) and `ex:mop2`
    (also reached by `ex:synth4`) through two blank nodes: hashing the
    synthesis alone, or the MOP alone, and `isinstance(chem_out, BNode)` ->
    `True` / `False` are rejected.
One mutant stays green, and it is equivalent: dropping `mop in selected` while
keeping the MOP-type test, since every node typed MetalOrganicPolyhedron is
selected by construction.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='build_link_graph',
    fixture="fixture.ttl",
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)

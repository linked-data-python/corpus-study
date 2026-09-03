"""Validation driver for INCATools__kgcl-rdflib__kgcl_rdflib_diff_owlstar_sublanguage.py__get_bnodes_2_triple_annotations.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

The fixture is part of the translation: it must hold several solutions of the
pattern the region reads, the zero-solution case, and neighbouring triples
that must NOT match.

`entry='demo'`, not `get_bnodes_2_triple_annotations` itself (see
original.py): the region returns a dict KEYED BY BNODE, and rdflib mints a
fresh internal id for every blank node on every parse -- run_pair calls the
fixture-loading callable once per side, so the two sides' graphs (and every
BNode in them) are never identity-comparable. `demo` repackages the result
into a sorted, bnode-identity-free structure first.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='demo',
    fixture="fixture.ttl",
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets. demo's
    # own output is already a canonical sorted list either way.
)

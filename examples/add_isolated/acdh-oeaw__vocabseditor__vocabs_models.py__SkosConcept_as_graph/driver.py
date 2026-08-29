"""Validation driver for acdh-oeaw__vocabseditor__vocabs_models.py__SkosConcept_as_graph.

Establishes semantic equivalence of original.py and translated.ldpy.
`demo` is the identical harness both files carry (see meta.json): as_graph
is a method body lifted out of its class, so `demo` builds the minimal
`self` (context_shim.SkosConceptStub) and returns the graph as_graph(self)
writes -- the region's only RDF-observable effect (meta.oracle: isomorphism).

Two scenarios: "with_broader" exercises `if self.broader_concept:`, a
non-empty notation, a narrower concept, a note (the `g = g + note.as_graph()`
reassignment this region's own body performs), a source, and all four
label_type branches. "top_concept" exercises the `else:` branch (both of its
triples, on two different subjects) and the empty-notation skip.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[(("with_broader",), {}), (("top_concept",), {})],
)

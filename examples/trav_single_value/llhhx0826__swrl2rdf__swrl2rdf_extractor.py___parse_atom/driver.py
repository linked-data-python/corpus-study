"""Validation driver for llhhx0826__swrl2rdf__swrl2rdf_extractor.py___parse_atom.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

_parse_atom takes four more arguments beyond the graph (atom_node,
prefix_map, var_names, reverse_mapping), so the default single-argument call
`run_pair` would build from `fixture=` alone does not fit -- `calls=` gives
one call per branch of the function: the five recognised SWRL atom shapes and
the unrecognised one that falls through to `return None`.  Every m{ }.first()
in the region is scoped to `{atom_node}`, and fixture.ttl carries a
neighbouring atom (atom7) with the same predicates to prove that scoping; one
of the calls (atom2) hits the zero-solution case on purpose (no
swrl:classPredicate triple at all), matching what g.value returns None for.
"""
from rdflib import URIRef

from rdfeval.harness import fixture_graph, run_pair
from context_shim import PrefixMap

EX = "http://example.org/"


def _call(atom_local, var_names=None):
    # prefix_map is built once, outside `make`, and shared by both sides: it
    # is read-only in _parse_atom (never mutated), and PrefixMap has no
    # __eq__ of its own (see context_shim, transcribed from the real class),
    # so two *equal but distinct* instances would otherwise be reported as
    # differing when the harness compares the arguments each side received.
    prefix_map = PrefixMap()
    var_names = dict(var_names or {})

    def make():
        graph = fixture_graph("fixture.ttl")
        return (
            (graph, URIRef(EX + atom_local), prefix_map, dict(var_names), None),
            {},
        )
    return make


VERDICT = run_pair(
    __file__,
    entry='_parse_atom',
    fixture="fixture.ttl",
    calls=[
        _call("atom1", {URIRef(EX + "varX"): "x"}),           # ClassAtom, full
        _call("atom2"),                                        # ClassAtom, classPredicate absent (zero solution)
        _call("atom3", {URIRef(EX + "varY"): "y"}),           # IndividualPropertyAtom, full
        _call("atom4", {URIRef(EX + "varZ"): "z"}),           # DatavaluedPropertyAtom, literal argument2
        _call("atom5", {URIRef(EX + "varW"): "w"}),           # BuiltinAtom, collection of 2 arguments
        _call("atom6"),                                        # no branch matches -> None
    ],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets. Each call
    # here returns a single dataclass instance (or None), not a sequence, so
    # ordering does not apply.
)

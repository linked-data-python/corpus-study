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


# --- Repair audit (2026-10-31) -------------------------------------------
# fixture_edge.ttl: zero / two solutions of the reads of every branch (a
# `.one()` or next(iter()) raises, or raises another message than the
# original's own ValueError), a decoy atom stored first (widened subject),
# an atom with two rdf:types, falsy literal arguments, and blank-node atoms
# inside an rdf:List as rules_from_graph walks them.  prefix_map is built
# the repository's way, PrefixMap.from_graph() on the parsed graph (shared
# by both sides, as above).  Every graph a call receives is recorded, so
# that the bindings each side leaves on it can be compared afterwards: the
# translation's `@graph graph` must not rebind what the caller's graph (its
# parsed @prefix header) already binds.
from rdflib.collection import Collection

import rdfeval.harness as _harness

EDGE = "fixture_edge.ttl"
EDGE_PM = PrefixMap.from_graph(fixture_graph(EDGE))
GRAPHS = []           # (case label, graph), one per side, original first


def _edge(atom_local=None, list_index=None, var_names=None):
    var_names = dict(var_names or {})
    label = atom_local or f"body[{list_index}]"

    def make():
        graph = fixture_graph(EDGE)
        GRAPHS.append((label, graph))
        if list_index is None:
            node = URIRef(EX + atom_local)
        else:
            head = graph.value(URIRef(EX + "body"), URIRef(EX + "atoms"))
            node = list(Collection(graph, head))[list_index]
        return ((graph, node, EDGE_PM, dict(var_names), None), {})
    return make


def _bindings_diffs():
    diffs = []
    for i in range(0, len(GRAPHS) - 1, 2):
        (label, go), (_, gt) = GRAPHS[i], GRAPHS[i + 1]
        bo = {(str(p), str(n)) for p, n in go.namespace_manager.namespaces()}
        bt = {(str(p), str(n)) for p, n in gt.namespace_manager.namespaces()}
        if not bo <= bt:
            diffs.append(f"{label}: prefix bindings lost by the translation: "
                         f"{sorted(bo - bt)}")
    return diffs


_captured = []
_real_emit = _harness._emit
_harness._emit = _captured.append     # one verdict line, emitted below
try:
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
            # repair audit, fixture_edge.ttl
            _edge("e1", var_names={URIRef(EX + "v1"): "a"}),       # two rdf:types, decoy stored first
            _edge("e2"),                                           # ClassAtom, no argument1 (raises)
            _edge("e3"),                                           # ClassAtom, two classPredicate / argument1
            _edge("e4", var_names={URIRef(EX + "v1"): "a"}),       # IndividualPropertyAtom, no propertyPredicate
            _edge("e5", var_names={URIRef(EX + "v1"): "a"}),       # IndividualPropertyAtom, two values
            _edge("e10"),                                          # IndividualPropertyAtom, no argument1 (raises)
            _edge("e11", var_names={URIRef(EX + "v1"): "a"}),      # IndividualPropertyAtom, no argument2 (raises)
            _edge("e6"),                                           # DatavaluedPropertyAtom, no argument2 (raises)
            _edge("e12"),                                          # DatavaluedPropertyAtom, no argument1 (raises)
            _edge("e13", var_names={URIRef(EX + "v1"): "a"}),      # DatavaluedPropertyAtom, two values of each read
            _edge("e14", var_names={URIRef(EX + "v1"): "a"}),      # DatavaluedPropertyAtom, no propertyPredicate
            _edge("e7"),                                           # argument2 ""
            _edge("e7b"),                                          # argument2 0
            _edge("e8"),                                           # BuiltinAtom, no builtin, no arguments
            _edge("e9", var_names={URIRef(EX + "v1"): "a"}),       # BuiltinAtom, two builtins, two lists
            _edge(list_index=0),                                   # blank-node ClassAtom in an rdf:List
            _edge(list_index=1),                                   # blank-node IndividualPropertyAtom
        ],
        # ordered=True only if the region imposes an order (sorted, ORDER BY):
        # no store promises one, so results are compared as multisets. Each call
        # here returns a single dataclass instance (or None), not a sequence, so
        # ordering does not apply.
    )
finally:
    _harness._emit = _real_emit

if VERDICT.get("error") is None:
    VERDICT["diffs"] = VERDICT.get("diffs", []) + _bindings_diffs()
    VERDICT["equivalent"] = not VERDICT["diffs"]
    VERDICT["bindings_compared"] = len(GRAPHS) // 2
_real_emit(VERDICT)

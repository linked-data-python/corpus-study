"""Validation driver for shijx12__KQAPro_Baselines__SPARQL_sparql_engine.py__SparqlEngine__new_fact_node.

_new_fact_node takes `self` (mutating self.graph) plus three terms h, r, t,
and returns a fresh BNode -- the oracle is self.graph's isomorphism after the
call (run_pair compares every call argument, self included, and self.graph
is compared through _Engine.__eq__ below) plus the returned BNode (compared
by kind only -- BNode identifiers differ between runs by construction).

Unlike a region where the graph is passed in as its own argument, self.graph
lives INSIDE self here, so self must be a FRESH object per side (sharing one
would merge both sides' triples into the same graph) -- hence _Engine.__eq__
compares by isomorphism rather than relying on identity, the way the sibling
region ObjectMinCardinality_to_rdf (same stratum, this lot) can.

Calls (what the repository really passes: SPARQL/sparql_engine.py:75 and 94,
inside __init__, always right after the same `graph.add((h, r, t))`, with
h and r taken from self.nodes (URIRef) and t either a URIRef from self.nodes
or the BNode that _get_value_node returns for an attribute value):

  1. h/r/t all IRIs -- a relation fact (line 94);
  2. t a literal -- kept from the first version of this driver; the
     repository never passes one (the tail of an attribute fact is the
     BNode of _get_value_node), it is a harmless extra shape;
  3. t a BNode and the engine's graph already holding the (h, r, t) triple
     -- an attribute fact (line 75), the real situation: the reification
     node is added next to a graph that is not empty, and must not disturb
     the existing triple;
  4. r an IRI built like the repository's `URIRef(legal(p))` (space ->
     underscore), on a seeded graph as in 3.

The three predicate keys (SparqlEngine.PRED_FACT_*) are plain str, as in the
repository (context_shim.py), and self.nodes maps them to URIRef, as
SparqlEngine.__init__ does.

Non-terms (t=None, t="plain", t=3) are NOT exercised: the original raises
AssertionError in graph.add where the translated `{t}` would coerce them
to a literal, but the repository cannot reach it (the line just above the
call, `graph.add((h, r, t))`, would already have raised). See meta.json,
repair.remaining.
"""
from rdflib import BNode, Graph, Literal, URIRef

from context_shim import SparqlEngine

from rdfeval.harness import graphs_isomorphic, run_pair

# As in SparqlEngine.__init__: nodes[p] = URIRef(legal(p)) for each special
# predicate p (a plain str key such as 'pred:fact_h').
NODES = {
    SparqlEngine.PRED_FACT_H: URIRef("pred:fact_h"),
    SparqlEngine.PRED_FACT_R: URIRef("pred:fact_r"),
    SparqlEngine.PRED_FACT_T: URIRef("pred:fact_t"),
}


class _Engine:
    """Minimal stand-in for the `self` _new_fact_node runs against: reads
    self.nodes (unchanged, shared read-only across both sides) and mutates
    self.graph. __eq__ compares self.graph by isomorphism -- see the module
    docstring on why identity comparison would not do."""

    def __init__(self, seed=()):
        self.nodes = dict(NODES)
        self.graph = Graph()
        for triple in seed:
            self.graph.add(triple)

    def __eq__(self, other):
        if not isinstance(other, _Engine):
            return NotImplemented
        return self.nodes == other.nodes and graphs_isomorphic(self.graph, other.graph)


def case(h, r, t, seeded=False):
    def factory():
        # a fresh BNode per side is fine: the comparison is by isomorphism
        tail = BNode() if t is BNODE else t
        seed = [(h, r, tail)] if seeded else ()
        return ((_Engine(seed), h, r, tail), {})
    return factory


def legal(s):
    # verbatim from SPARQL/sparql_engine.py:16
    return s.replace(' ', '_')


BNODE = object()   # sentinel: "a fresh BNode for t, on each side"


VERDICT = run_pair(
    __file__,
    entry="_new_fact_node",
    calls=[
        case(URIRef("http://example.org/e1"),
             URIRef("http://example.org/rel1"),
             URIRef("http://example.org/e2")),
        case(URIRef("http://example.org/e3"),
             URIRef("http://example.org/rel2"),
             Literal("some text")),
        case(URIRef("http://example.org/e4"),
             URIRef("http://example.org/attr_1"),
             BNODE, seeded=True),
        case(URIRef("http://example.org/e5"),
             URIRef(legal("http://example.org/has part of")),
             URIRef("http://example.org/e6"), seeded=True),
    ],
)

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

Two calls: one where h/r/t are all IRIs (a fact about two entities and a
relation), one where t is a literal (a fact whose tail is a value -- the
other shape _new_fact_node is used for in the source project).
"""
from rdflib import Graph, Literal, URIRef

from context_shim import SparqlEngine

from rdfeval.harness import graphs_isomorphic, run_pair

NODES = {
    SparqlEngine.PRED_FACT_H: URIRef("http://example.org/kqapro#pred_h"),
    SparqlEngine.PRED_FACT_R: URIRef("http://example.org/kqapro#pred_r"),
    SparqlEngine.PRED_FACT_T: URIRef("http://example.org/kqapro#pred_t"),
}


class _Engine:
    """Minimal stand-in for the `self` _new_fact_node runs against: reads
    self.nodes (unchanged, shared read-only across both sides) and mutates
    self.graph. __eq__ compares self.graph by isomorphism -- see the module
    docstring on why identity comparison would not do."""

    def __init__(self):
        self.nodes = dict(NODES)
        self.graph = Graph()

    def __eq__(self, other):
        if not isinstance(other, _Engine):
            return NotImplemented
        return self.nodes == other.nodes and graphs_isomorphic(self.graph, other.graph)


def case(h, r, t):
    def factory():
        return ((_Engine(), h, r, t), {})
    return factory


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
    ],
)

"""Validation driver for ktbs__ktbs__lib_rdfrest_util_proxystore.py__ProxyStore_query.

Establishes semantic equivalence of original.py and translated.ldpy.

The region is a pass-through method: it forwards an opaque query string,
and the ``initNs``/``initBindings`` dicts, to ``self._graph.query(...)``.
There is no RDF pattern written in the region itself for an island to
capture, so ``entry='query'`` is called on a minimal stand-in object that
provides ``_pull()`` and ``_graph`` (a real rdflib Graph with a couple of
triples), with a real SPARQL query string and non-trivial initNs/
initBindings, so the pass-through is genuinely exercised.
"""
from rdflib import Graph, Namespace, URIRef, Literal
from rdfeval.harness import run_pair, graphs_isomorphic

EX = Namespace("http://example.org/")


class _FakeStore:
    """Minimal stand-in for ProxyStore: only what `query` touches."""

    def __init__(self):
        self._pulled = False
        self._graph = Graph()
        self._graph.add((EX.alice, EX.knows, EX.bob))
        self._graph.add((EX.bob, EX.knows, EX.carol))

    def _pull(self):
        self._pulled = True

    def __eq__(self, other):
        # The harness compares call arguments too (mutable arguments are
        # part of the region's observable effect); two independently built
        # stand-ins are equal here iff `_pull` was called on both and their
        # graphs are isomorphic.
        if not isinstance(other, _FakeStore):
            return NotImplemented
        return self._pulled == other._pulled and \
            graphs_isomorphic(self._graph, other._graph)

    def __hash__(self):
        return id(self)


def _case():
    self_o = _FakeStore()
    query = "SELECT ?o WHERE { ?s ?p ?o }"
    init_ns = {"ex": EX}
    init_bindings = {"s": URIRef("http://example.org/alice")}
    return (self_o, query), {"initNs": init_ns, "initBindings": init_bindings}


VERDICT = run_pair(
    __file__,
    entry='query',
    calls=[_case],
)

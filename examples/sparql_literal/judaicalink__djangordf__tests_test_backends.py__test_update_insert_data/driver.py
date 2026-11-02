"""Driver for judaicalink__djangordf__tests_test_backends.py__test_update_insert_data.

The region is a pytest test whose whole effect is an assertion, so each call
shows its outcome: a return of None (the assertion held) or the raised
AssertionError, compared like a value.  Backends are the context shim's
InMemoryBackend (the `backend` fixture of the source tests), fresh per call.

  empty            the fixture's case: INSERT DATA adds one triple, len == 1.
  same_triple      the graph already holds the very triple the update inserts:
                   still one triple, the assertion holds.
  other_object     the graph holds s p "w": the update must insert "v", so two
                   triples and the assertion fails (a translation that wrote a
                   different object, or nothing, would not fail the same way).
  other_subject    a neighbouring triple on another subject: two triples, fails.
  named_graph      a triple in a named graph only: the CONSTRUCT sees the
                   union of the graphs, so two triples, fails.
  update_ignored   a backend whose update does nothing: len == 0, fails.
  query_ignored    a backend whose query always returns an empty graph: fails.
"""
from rdflib import Graph, Literal, URIRef

from rdfeval.harness import run_pair
from djangordf_shim import InMemoryBackend

S = URIRef("http://example.org/s")
P = URIRef("http://example.org/p")


def _backend(*triples, graph=None):
    def make():
        b = InMemoryBackend()
        if triples:
            b.add(list(triples), graph=graph)
        return (b,), {}
    return make


class _UpdateIgnored(InMemoryBackend):
    def update(self, sparql):
        return None


class _QueryIgnored(InMemoryBackend):
    def query(self, sparql):
        return Graph()


CALLS = [
    _backend(),                                                       # empty
    _backend((S, P, Literal("v"))),                                   # same_triple
    _backend((S, P, Literal("w"))),                                   # other_object
    _backend((URIRef("http://example.org/s2"), P, Literal("v"))),     # other_subject
    _backend((S, P, Literal("v2")), graph=URIRef("http://example.org/g")),  # named_graph
    lambda: ((_UpdateIgnored(),), {}),                                # update_ignored
    lambda: ((_QueryIgnored(),), {}),                                 # query_ignored
]

VERDICT = run_pair(
    __file__,
    entry='test_update_insert_data',
    calls=CALLS,
)

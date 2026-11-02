"""Validation driver for StoreTestCase.testNamedGraphUpdateWithInitBindings
(rdflib-leveldb).

The region is a test method: its whole effect is `INSERT { ?a ?b ?c } WHERE {}`
run on the context `urn:graph` of `self.graph`, then an assertEqual that the
context holds exactly (michel, likes, pizza).  `self` is a plain stub (no
`__eq__`, so the harness compares its graph, context by context): a
ConjunctiveGraph on the Memory store, `store` the name the log line prints,
and an `assertEqual` that raises AssertionError like unittest's.

Calls, each on a fresh stub:

  * empty store: the update writes the triple, the assert passes (None);
  * `urn:graph` already holding an unrelated triple: the assert FAILS, so a
    translation that dropped or widened the update shows (AssertionError);
  * `urn:graph` already holding the very triple: the assert passes;
  * another context and the default graph holding triples: neither is touched
    (the update is scoped to `urn:graph`), assert passes; the stub graph is
    compared afterwards, so a write to the wrong context shows;
  * the graph `urn:graph` holding a different object for the same
    (michel, likes) pair: the assert fails.

The duration the method logs (`{t1 - t0:.5f}`) is the only text that is not the
program's meaning: the filter blanks it on both sides.
"""
import logging
import re
import warnings

from rdflib import ConjunctiveGraph, URIRef

from rdfeval.harness import run_pair

GRAPH = URIRef("urn:graph")
OTHER = URIRef("urn:other")
MICHEL = URIRef("urn:michel")
LIKES = URIRef("urn:likes")


class _Self:
    store = "Memory"

    def __init__(self, triples=()):
        self.graph = ConjunctiveGraph("Memory")
        for s, p, o, ctx in triples:
            if ctx is None:
                self.graph.add((s, p, o))
            else:
                self.graph.get_context(ctx).add((s, p, o))

    def assertEqual(self, first, second, msg=None):
        if first != second:
            raise AssertionError(msg or f"{first!r} != {second!r}")


def call(*triples):
    return lambda: ((_Self(triples),), {})


warnings.simplefilter("ignore", DeprecationWarning)
logging.getLogger().setLevel(logging.DEBUG)

VERDICT = run_pair(
    __file__,
    entry='testNamedGraphUpdateWithInitBindings',
    calls=[
        call(),
        call((URIRef("urn:bob"), LIKES, URIRef("urn:sushi"), GRAPH)),
        call((MICHEL, LIKES, URIRef("urn:pizza"), GRAPH)),
        call((URIRef("urn:bob"), LIKES, URIRef("urn:sushi"), OTHER),
             (URIRef("urn:alice"), LIKES, URIRef("urn:tea"), None)),
        call((MICHEL, LIKES, URIRef("urn:pasta"), GRAPH)),
    ],
    stdout_filter=lambda text: re.sub(r"\d+\.\d{5}", "<duration>", text),
)

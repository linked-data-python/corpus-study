# Context shim (see meta.json): subset of djangordf/backends/memory.py from
# judaicalink/djangordf@494eedbeba (the `backend` pytest fixture of
# tests/test_backends.py returns InMemoryBackend()), so the region executes
# without the djangordf package. Identical for both representations.
from rdflib import ConjunctiveGraph, URIRef


class InMemoryBackend:
    """Triple-store backend that keeps all data in process memory."""

    def __init__(self):
        self._store = ConjunctiveGraph()

    def query(self, sparql):
        result = self._store.query(sparql)
        if result.type in ("CONSTRUCT", "DESCRIBE") and result.graph is not None:
            return result.graph
        return result

    def update(self, sparql):
        self._store.update(sparql)

    def add(self, triples, graph=None):
        target = self._target(graph)
        for triple in triples:
            target.add(triple)

    def _target(self, graph):
        if graph is None:
            return self._store.default_context
        return self._store.get_context(graph)

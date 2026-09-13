# Context shim (see meta.json): a minimal in-memory stand-in for the
# Oxigraph class from naas_abi_core/services/triple_store/adaptors/secondary/Oxigraph.py
# (jupyter-naas/abi@3fb7f5304d), whose real __init__ opens an HTTP connection
# to a live Oxigraph server -- unavailable outside the project. This shim
# keeps the SAME method signatures and RDF semantics (named-graph store,
# SPARQL query returning an rdflib Result, CONSTRUCT-shaped subject graph)
# but backs them with an in-process rdflib ConjunctiveGraph instead of HTTP,
# so both representations of the extracted region run identically.
from rdflib import ConjunctiveGraph, Graph


class Oxigraph:
    def __init__(self, oxigraph_url=None, timeout=60):
        self.oxigraph_url = oxigraph_url
        self._store = ConjunctiveGraph()

    def insert(self, triples, graph_name):
        named = self._store.get_context(graph_name)
        for t in triples:
            named.add(t)

    def query(self, query):
        return self._store.query(query)

    def get_subject_graph(self, subject, graph_name):
        named = self._store.get_context(graph_name)
        out = Graph()
        for p, o in named.predicate_objects(subject):
            out.add((subject, p, o))
        return out

    def remove(self, triples, graph_name):
        named = self._store.get_context(graph_name)
        for t in triples:
            named.remove(t)

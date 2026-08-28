# Context shim (see meta.json) for cognitedata/neat@4042d3e96d: the two
# bindings the region imports, reduced to what it exercises.
#
#   NAMED_GRAPH_NAMESPACE : cognite/neat/_v0/core/_constants.py:278, verbatim.
#   NeatInstanceStore     : cognite/neat/_v0/core/_store/_instance.py:38 --
#       only __init__, from_oxi_local_store, graph, named_graphs,
#       _add_triples and diff are kept, with the bodies of the upstream
#       methods (including the CLEAR SILENT GRAPH updates and the
#       FILTER NOT EXISTS diff query of _instances/queries/_select.py:454).
#       The provenance/issue-list/transformer machinery is dropped.
#       from_oxi_local_store falls back to rdflib's in-memory Dataset
#       because oxrdflib is not installed in the eval environment; the
#       behaviour under test (named-graph diffing) is store-independent.
#
# Identical for both representations.
from rdflib import Dataset, Namespace, URIRef
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID

NAMED_GRAPH_NAMESPACE = Namespace("http://thisisneat.io/namedgraph/")


class NeatInstanceStore:
    def __init__(self, dataset, default_named_graph=None):
        self.dataset = dataset
        self.default_named_graph = default_named_graph or DATASET_DEFAULT_GRAPH_ID

    @classmethod
    def from_oxi_local_store(cls, storage_dir=None):
        return cls(dataset=Dataset())

    def graph(self, named_graph=None):
        """Get named graph from the dataset to query over"""
        return self.dataset.graph(named_graph or self.default_named_graph)

    @property
    def named_graphs(self):
        return [context.identifier for context in self.dataset.contexts()]

    def _add_triples(self, triples, named_graph, batch_size=10_000):
        graph = self.graph(named_graph)
        for triple in triples:
            graph.add(triple)

    def _get_graph_diff(self, source_graph, target_graph):
        query = f"""
        SELECT ?s ?p ?o
        WHERE {{
        GRAPH <{source_graph}> {{ ?s ?p ?o }}
        FILTER NOT EXISTS {{
            GRAPH <{target_graph}> {{ ?s ?p ?o }}
        }}
        }}
        """
        return list(self.dataset.query(query))

    def diff(self, current_named_graph: URIRef, new_named_graph: URIRef) -> None:
        if current_named_graph not in self.named_graphs:
            raise ValueError(f"Current named graph not found: {current_named_graph}")
        if new_named_graph not in self.named_graphs:
            raise ValueError(f"New named graph not found: {new_named_graph}")

        self.dataset.update(f"CLEAR SILENT GRAPH <{NAMED_GRAPH_NAMESPACE['DIFF_ADD']}>")
        self.dataset.update(f"CLEAR SILENT GRAPH <{NAMED_GRAPH_NAMESPACE['DIFF_DELETE']}>")

        self._add_triples(
            self._get_graph_diff(new_named_graph, current_named_graph),
            named_graph=NAMED_GRAPH_NAMESPACE["DIFF_ADD"],
        )
        self._add_triples(
            self._get_graph_diff(current_named_graph, new_named_graph),
            named_graph=NAMED_GRAPH_NAMESPACE["DIFF_DELETE"],
        )

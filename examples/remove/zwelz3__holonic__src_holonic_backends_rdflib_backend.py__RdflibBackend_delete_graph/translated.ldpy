# Extracted from zwelz3/holonic@d8d1758752 : src/holonic/backends/rdflib_backend.py
# region: RdflibBackend.delete_graph (lines 98-102, stratum remove)
# licence of the source repository: see meta.json
from rdflib import Dataset, Graph, Literal, URIRef

def delete_graph(self, graph_iri: str) -> None:
    """Remove named graph from the dataset."""
    g = self.ds.graph(URIRef(graph_iri))
    g.remove((None, None, None))
    self.ds.remove_graph(g)

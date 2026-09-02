# Context shim (see meta.json): minimal reimplementation of the two helpers
# used by get_available_layers in ScaDS/KGpipe@67ca171cfd :
# src/kgpipe_view/owl_to_mermaid.py, so the region executes standalone.
# Identical bindings for both representations.
from rdflib import Graph


def _load_graph(ttl_path) -> Graph:
    g = Graph()
    g.parse(str(ttl_path), format="turtle")
    return g


def _local_name(uri) -> str:
    s = str(uri)
    if "#" in s:
        return s.rsplit("#", 1)[1]
    return s.rsplit("/", 1)[1]

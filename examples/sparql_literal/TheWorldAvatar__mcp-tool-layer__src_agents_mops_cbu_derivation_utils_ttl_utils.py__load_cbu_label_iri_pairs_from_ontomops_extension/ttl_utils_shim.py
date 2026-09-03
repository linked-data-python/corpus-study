# Context shim (see meta.json): sibling helper from the SAME source file,
# TheWorldAvatar/mcp-tool-layer@c440a33e08 :
# src/agents/mops/cbu_derivation/utils/ttl_utils.py -- the extractor keeps
# only the region's own IMPORTS as context, not sibling function
# definitions in the same module, so `load_graph_from_file` (called by the
# region but defined a few lines above it in the real file) is restored
# here verbatim (AGENT_BATCH.md, "163 regions ... restore the binding").
# Identical bindings for both representations.
import os

from rdflib import Graph


def load_graph_from_file(path: str) -> Graph:
    g = Graph()
    if os.path.exists(path):
        g.parse(path, format="turtle")
    return g

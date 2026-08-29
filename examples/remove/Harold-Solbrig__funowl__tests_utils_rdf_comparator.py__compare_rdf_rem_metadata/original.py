# Extracted from Harold-Solbrig/funowl@69e1cbe2f6 : tests/utils/rdf_comparator.py
# region: compare_rdf.rem_metadata (lines 80-85, stratum remove)
# licence of the source repository: see meta.json
from rdflib import Graph, RDFS, RDF, OWL, BNode
from rdflib.compare import to_isomorphic, IsomorphicGraph, graph_diff

def rem_metadata(g: Graph) -> IsomorphicGraph:
    # Remove list declarations from target
    for s in g.subjects(RDF.type, RDF.List):
        g.remove((s, RDF.type, RDF.List))
    g_iso = to_isomorphic(g)
    return g_iso

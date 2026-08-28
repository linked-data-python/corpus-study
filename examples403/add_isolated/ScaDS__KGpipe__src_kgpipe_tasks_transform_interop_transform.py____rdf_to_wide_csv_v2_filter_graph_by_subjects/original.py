# Extracted from ScaDS/KGpipe@67ca171cfd : src/kgpipe_tasks/transform_interop/transform.py
# region: __rdf_to_wide_csv_v2.filter_graph_by_subjects (lines 74-79, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, RDF

def filter_graph_by_subjects(graph: Graph, subjects: set):
    new_graph = Graph()
    for s, p, o in graph:
        if str(s) in subjects:
            new_graph.add((s, p, o))
    return new_graph

# Extracted from jorge-martinez-gil/dataq@0808bf5696 : dataq/metrics/licensing.py
# region: licensing (lines 16-25, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib import Graph, RDF
from ..namespaces import DCAT, DCT

def licensing(graph: Graph) -> float:
    licensed = 0
    total = 0
    for subject in graph.subjects(RDF.type, DCAT.Dataset):
        total += 1
        if any(graph.triples((subject, DCT.license, None))):
            licensed += 1
    if total == 0:
        return 0.0
    return (licensed / total) * 100

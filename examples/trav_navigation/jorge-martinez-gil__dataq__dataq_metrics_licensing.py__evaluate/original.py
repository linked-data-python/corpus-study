# Extracted from jorge-martinez-gil/dataq@0808bf5696 : dataq/metrics/licensing.py
# region: evaluate (lines 28-43, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, RDF
from ..namespaces import DCAT, DCT
from ..report import MetricResult

def evaluate(graph: Graph) -> MetricResult:
    licensed = 0
    total = 0
    for subject in graph.subjects(RDF.type, DCAT.Dataset):
        total += 1
        if any(graph.triples((subject, DCT.license, None))):
            licensed += 1
    value = 0.0 if total == 0 else (licensed / total) * 100
    return MetricResult(
        key="licensing",
        name="Licensing",
        value=value,
        unit="percent",
        higher_is_better=True,
        details={"datasets": total, "licensed_datasets": licensed},
    )

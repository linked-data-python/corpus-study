# Extracted from jupyter-naas/abi@3fb7f5304d : libs/naas-abi-marketplace/naas_abi_marketplace/domains/personnel/apps/cockpit/process_class_catalog.py
# region: _class_label (lines 50-54, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef
from rdflib.namespace import OWL, RDF, RDFS
_ABI_CLASS_LABELS: dict[str, str] = {
    f"{ABI_NS}Person": "Person",
    f"{ABI_NS}Organization": "Organization",
    f"{ABI_NS}Site": "Site",
    f"{ABI_NS}TemporalRegion": "Temporal Region",
    f"{ABI_NS}TemporalInstant": "Temporal Instant",
}

def _class_label(graph: Graph, class_uri: URIRef) -> str | None:
    label = graph.value(class_uri, RDFS.label)
    if label is not None:
        return str(label)
    return _ABI_CLASS_LABELS.get(str(class_uri))

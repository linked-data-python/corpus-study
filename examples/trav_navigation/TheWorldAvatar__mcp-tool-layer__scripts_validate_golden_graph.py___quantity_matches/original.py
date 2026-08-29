# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : scripts/validate_golden_graph.py
# region: _quantity_matches (lines 56-67, stratum trav_navigation)
# licence of the source repository: see meta.json
from typing import Any
from rdflib import Graph, Namespace, RDF, RDFS
ONTOSYN = Namespace("https://www.theworldavatar.com/kg/OntoSyn/")
OM2 = Namespace("http://www.ontology-of-units-of-measure.org/resource/om-2/")

def _quantity_matches(graph: Graph, step: Any, predicate_local: str, value: float, unit_local: str) -> bool:
    predicate = getattr(ONTOSYN, predicate_local)
    for quantity in graph.objects(step, predicate):
        raw_value = next(graph.objects(quantity, OM2.hasNumericalValue), None)
        raw_unit = next(graph.objects(quantity, OM2.hasUnit), None)
        try:
            numeric_ok = abs(float(raw_value) - float(value)) < 1e-6
        except Exception:
            numeric_ok = False
        if numeric_ok and _local_name(raw_unit) == unit_local:
            return True
    return False

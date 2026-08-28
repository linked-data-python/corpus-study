# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : src/pipelines/main_kg_building/build.py
# region: _find_step_node_for_hint (lines 1918-1937, stratum trav_existence)
# licence of the source repository: see meta.json
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS

def _find_step_node_for_hint(g: Graph, hint: dict[str, Any]) -> Optional[URIRef]:
    step_ref = str(hint.get("step_ref") or "").strip()
    type_local = str(hint.get("type_local") or "").strip()
    order = hint.get("order")
    candidates: list[URIRef] = []
    for node in (
        g.subjects(RDFS.label, Literal(step_ref))
        if step_ref
        else g.subjects(None, None)
    ):
        if not isinstance(node, URIRef):
            continue
        if type_local and not any(
            _local_name(t) == type_local for t in g.objects(node, RDF.type)
        ):
            continue
        if order is not None and not _step_has_order(g, node, order):
            continue
        candidates.append(node)
    return sorted(set(candidates), key=str)[0] if candidates else None

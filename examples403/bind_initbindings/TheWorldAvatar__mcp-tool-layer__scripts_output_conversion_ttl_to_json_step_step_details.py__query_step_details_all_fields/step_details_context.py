# Context shim (see meta.json): `_local_name`, `_camelize` and
# `query_step_type_label`, copied verbatim from
# scripts/output_conversion_ttl_to_json/step/step_details.py in
# TheWorldAvatar/mcp-tool-layer@c440a33e08 (the same file the extracted
# region comes from), so the region executes outside its module. Identical
# bindings for both representations -- this file is imported by both
# original.py and translated.ldpy, and is plain Python (no ldpy) in both
# cases, exactly like the upstream source: `query_step_type_label` is
# itself an instance of this stratum's idiom (initBindings, FILTER(?step =
# ?S)) but it is context, not the assigned region, so it is not translated.
from typing import List

from rdflib import Graph, URIRef


def _local_name(uri: str) -> str:
    if "#" in uri:
        return uri.rsplit("#", 1)[-1]
    return uri.rstrip("/").rsplit("/", 1)[-1]


def _camelize(name: str) -> str:
    if not name:
        return name
    out = name[0].lower() + name[1:]
    return out


def query_step_type_label(graph: Graph, step_uri: str) -> str:
    """Return simple type label for a step (e.g., Add, HeatChill, Sonicate)."""
    q = """
    PREFIX ontosyn: <https://www.theworldavatar.com/kg/OntoSyn/>
    SELECT DISTINCT ?t WHERE {
      ?step a ?t .
      FILTER(?step = ?S)
      FILTER(STRSTARTS(STR(?t), "https://www.theworldavatar.com/kg/OntoSyn/"))
    }
    """
    results = list(graph.query(q, initBindings={"S": URIRef(step_uri)}))
    # Prefer a type that is not ontosyn:SynthesisStep
    preferred: List[str] = []
    fallback: List[str] = []
    for row in results:
        t_uri = str(row.t)
        if t_uri.rstrip("/").endswith("/SynthesisStep"):
            fallback.append(t_uri)
        else:
            preferred.append(t_uri)
    if preferred:
        return _local_name(preferred[0])
    if fallback:
        # When the only type is the generic SynthesisStep, return a safer placeholder 'Step'
        return "Step"
    return "Step"

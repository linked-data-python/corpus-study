# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : scripts/output_conversion_ttl_to_json/step/step_details.py
# region: query_step_type_label (lines 26-51, stratum sparql_literal)
# licence of the source repository: see meta.json
from typing import Any, Dict, List
from rdflib import Graph, URIRef

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

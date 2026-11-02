# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : scripts/output_conversion_ttl_to_json/ontosynthesis_step_conversion.py
# region: query_step_details (lines 574-574, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib import URIRef
from step_conversion_context import graph, step_uri, vessel_type_query

vessel_type_result = list(graph.query(vessel_type_query, initBindings={'step': URIRef(step_uri)}))

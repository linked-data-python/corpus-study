# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : scripts/output_conversion_ttl_to_json/ontosynthesis_chemicals_conversion.py
# region: query_synthesis_outputs (lines 253-253, stratum sparql_literal)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef

results = graph.query(query, initBindings={'synthesis': URIRef(synthesis_uri)})

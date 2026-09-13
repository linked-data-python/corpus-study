# Context shim (see meta.json): the region calls a helper `_select_uris`
# defined elsewhere in TheWorldAvatar/mcp-tool-layer's
# scripts/output_conversion_ttl_to_json/ontosynthesis_characterisation_conversion.py
# that the extracted lines do not include. Reconstructed here, minimal, so
# the region executes outside the module: run a SPARQL SELECT projecting a
# single ?uri variable and collect the bound URIRefs. Identical bindings for
# both representations.
from rdflib import URIRef


def _select_uris(graph, query):
    return [URIRef(str(row.uri)) for row in graph.query(query)]

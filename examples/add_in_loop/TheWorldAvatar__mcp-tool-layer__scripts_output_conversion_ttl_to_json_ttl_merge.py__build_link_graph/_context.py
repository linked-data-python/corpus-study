# Context shim (see meta.json): subset of
# scripts/output_conversion_ttl_to_json/ttl_merge.py from
# TheWorldAvatar/mcp-tool-layer@c440a33e08, so the region executes outside
# the module (build_link_graph calls a module-level helper it does not
# define). Identical bindings for both representations.
from rdflib import Graph


def _bind_prefixes(g: Graph) -> None:
    g.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    g.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
    g.bind("ontosyn", "https://www.theworldavatar.com/kg/OntoSyn/")
    g.bind("ontomops", "https://www.theworldavatar.com/kg/ontomops/")
    g.bind("ontospecies", "http://www.theworldavatar.com/ontology/ontospecies/OntoSpecies.owl#")

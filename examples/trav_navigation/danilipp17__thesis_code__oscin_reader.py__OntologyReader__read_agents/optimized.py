# Extracted from danilipp17/thesis_code@c2772e3555 : oscin/reader.py
# region: OntologyReader._read_agents (lines 257-266, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef
from rdflib.namespace import OWL, RDF, RDFS, XSD
from shim_namespaces import (
    AGENTO,
    AGENTOSCIN,
    CALLS_CREW,
    COORD_CUSTOM,
    COORD_SEQUENTIAL,
    HAS_DESCRIPTION,
    HAS_TITLE,
)

# Context restored (meta.json): self.g is the instance graph, agent_uri and
# _rp_type_map are set up by the enclosing method before this statement.
# Populator writes exactly one employsReasoningPattern triple per agent, but
# the rp individual can carry more than one rdf:type (its own class plus
# owl:NamedIndividual, superclasses, ...), which is why the inner loop scans
# several types and stops at the first one the map recognises.


class _Self:
    def __init__(self, g):
        self.g = g


g = Graph()
agent_uri = URIRef("http://example.org/agent/1")
rp_uri = URIRef("http://example.org/rp/1")
g.add((agent_uri, AGENTOSCIN.employsReasoningPattern, rp_uri))
g.add((rp_uri, RDF.type, OWL.NamedIndividual))
g.add((rp_uri, RDF.type, AGENTOSCIN.ReAct))

self = _Self(g)
_rp_type_map = {
    str(AGENTOSCIN.ReAct): "ReAct",
    str(AGENTOSCIN.ChainOfThought): "ChainOfThought",
    str(AGENTOSCIN.ReflectionLoop): "ReflectionLoop",
    str(AGENTOSCIN.TreeOfThoughts): "TreeOfThoughts",
}
reasoning_pattern = ""

for rp_uri in self.g.objects(agent_uri, AGENTOSCIN.employsReasoningPattern):
    for rp_type in self.g.objects(rp_uri, RDF.type):
        reasoning_pattern = _rp_type_map.get(str(rp_type), "")
        if reasoning_pattern:
            break
    if reasoning_pattern:
        break

print(reasoning_pattern)

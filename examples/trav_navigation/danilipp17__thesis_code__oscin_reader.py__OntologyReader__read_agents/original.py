# Extracted from danilipp17/thesis_code@c2772e3555 : oscin/reader.py
# region: OntologyReader._read_agents (lines 257-266, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib.namespace import OWL, RDF, RDFS, XSD
from oscin.namespaces import (
    AGENTO,
    AGENTOSCIN,
    CALLS_CREW,
    COORD_CUSTOM,
    COORD_SEQUENTIAL,
    HAS_DESCRIPTION,
    HAS_TITLE,
)

for rp_uri in self.g.objects(
    agent_uri, AGENTOSCIN.employsReasoningPattern
):
    for rp_type in self.g.objects(rp_uri, RDF.type):
        name = _rp_type_map.get(str(rp_type))
        if name:
            reasoning_pattern = name
            break
    if reasoning_pattern:
        break

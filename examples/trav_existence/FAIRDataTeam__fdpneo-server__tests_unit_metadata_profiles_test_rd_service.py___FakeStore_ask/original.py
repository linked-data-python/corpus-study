# Extracted from FAIRDataTeam/fdpneo-server@3e72e119ae : tests/unit/metadata/profiles/test_rd_service.py
# region: _FakeStore.ask (lines 117-124, stratum trav_existence)
# licence of the source repository: see meta.json
import re
from rdflib import Graph, URIRef
from rdflib.namespace import RDF
from fdpneo_server.shared.namespaces import FDP_RESOURCE_DEFINITION, SH

async def ask(self, sparql: str) -> bool:
    # Used by schema_exists: does the named graph hold a SHACL shape?
    match = re.search(r"GRAPH <([^>]+)>", sparql)
    assert match is not None
    graph = self.graphs.get(match.group(1), Graph())
    has_node_shape = (None, RDF.type, SH.NodeShape) in graph
    has_target_class = any(graph.triples((None, SH.targetClass, None)))
    return has_node_shape or has_target_class

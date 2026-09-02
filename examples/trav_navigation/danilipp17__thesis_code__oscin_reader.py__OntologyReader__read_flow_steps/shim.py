# Context shim (see meta.json): minimal reconstruction of the
# OntologyReader instance state (self.g, self._str_value / self._int_value /
# self._local_name, self._agent_uri_to_key) used by
# OntologyReader._read_flow_steps in danilipp17/thesis_code@c2772e3555 :
# oscin/reader.py, plus HAS_TITLE/CALLS_CREW (imported from oscin.namespaces,
# unavailable here) and the starting bindings, so the region executes
# standalone. Identical bindings for both representations.
from pathlib import Path
from rdflib import Graph, URIRef

AGENTO_NS = "http://www.w3id.org/agentic-ai/onto#"
HAS_TITLE = URIRef(AGENTO_NS + "hasTitle")
CALLS_CREW = URIRef(AGENTO_NS + "callsCrew")


class _Reader:
    def __init__(self, graph, agent_uri_to_key):
        self.g = graph
        self._agent_uri_to_key = agent_uri_to_key

    def _str_value(self, subject, prop):
        v = self.g.value(subject, prop)
        return str(v) if v is not None else None

    def _int_value(self, subject, prop):
        v = self.g.value(subject, prop)
        return int(v) if v is not None else None

    def _local_name(self, uri):
        s = str(uri)
        if "#" in s:
            return s.rsplit("#", 1)[1]
        return s.rsplit("/", 1)[1]


def build_fixture():
    graph = Graph()
    graph.parse(str(Path(__file__).resolve().parent / "fixture.ttl"),
                format="turtle")
    agent_uri_to_key = {
        "http://example.org/agents#researcher": "researcher_agent",
    }
    reader = _Reader(graph, agent_uri_to_key)
    wp_uri = URIRef("http://example.org/workflows#WP1")
    return reader, wp_uri

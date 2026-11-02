"""Validation driver for comp-rob2b__kindyngen__kindynsyn_synthesizer_synthesizer.py__TreeExpander_expand.

`expand` is a method of TreeExpander and only reads `self.graph` and
`self.expanders` (query text -> CompiledExpander, the shim's verbatim
class), so `self` is a stub with those two attributes; the graph is parsed
from fixture.ttl for each call.  Four expander queries (see the fixture):
a direct one, a property-path one, one that finds the same child through two
paths, and one that matches nothing.

Calls: ex:a (children b via two queries, c via two queries and twice in one,
e; the neighbours of ex:z never), ex:b (only its own child d), ex:d and an
unknown node (no child: {}), and a TreeExpander with no expander at all.
"""
from pathlib import Path

from rdfeval.harness import fixture_graph, run_pair

from kindyngen_context import CompiledExpander

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
EX = "http://example.org/"
PFX = f"PREFIX ex: <{EX}>\n"

Q_DIRECT = PFX + "SELECT ?child WHERE { ?node ex:hasChild ?child }"
Q_PART = PFX + "SELECT ?child WHERE { ?node ex:hasPart/ex:hasChild ?child }"
Q_LINK = PFX + "SELECT ?child WHERE { ?node ex:link ?x . ?x ex:to ?child }"
Q_SENSORS = PFX + "SELECT ?child WHERE { ?node ex:hasSensor ?child }"


class _TreeExpander:
    def __init__(self, queries):
        self.graph = fixture_graph(FIXTURE)
        self.expanders = {q: CompiledExpander(q) for q in queries}


def call(node, queries=(Q_DIRECT, Q_PART, Q_LINK, Q_SENSORS)):
    from rdflib import URIRef

    def _make():
        return (_TreeExpander(queries), URIRef(EX + node)), {}
    return _make


VERDICT = run_pair(
    __file__,
    entry='expand',
    calls=[call("a"), call("b"), call("d"), call("unknown"), call("a", ())],
    ordered=False,
)

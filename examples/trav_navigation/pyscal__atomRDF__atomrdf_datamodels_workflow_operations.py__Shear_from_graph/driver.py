"""Driver for Shear.from_graph (atomRDF).

`from_graph(cls, graph, activity_id)` is called with the shim's Shear as
`cls` and the fixture graph; the returned Shear instances are compared
attribute by attribute.  One call per activity of fixture.ttl, plus an
activity given as a plain string (get_sample_object coerces it), an activity
that is not in the graph, and an empty graph.
"""
from pathlib import Path

from rdflib import Graph, Namespace

from atomrdf_context import Shear
from rdfeval.harness import fixture_graph, run_pair

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
EX = Namespace("http://example.org/")


def call(activity, empty=False):
    def make():
        graph = Graph() if empty else fixture_graph(FIXTURE)
        return (Shear, graph, activity), {}
    return make


CALLS = [call(EX[f"act{i}"]) for i in range(1, 8)]
CALLS += [
    call("http://example.org/act1"),     # a str is coerced to a URIRef
    call(EX.unknown),                    # an activity the graph does not know
    call(EX.act1, empty=True),           # an empty graph
]

VERDICT = run_pair(__file__, entry="from_graph", fixture="fixture.ttl", calls=CALLS)

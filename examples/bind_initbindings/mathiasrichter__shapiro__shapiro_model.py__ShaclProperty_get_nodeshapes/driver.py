"""Validation driver for mathiasrichter__shapiro__shapiro_model.py__ShaclProperty_get_nodeshapes.

Establishes semantic equivalence of original.py and translated.ldpy.

get_nodeshapes reads a graph reachable through ``self.graph`` and returns a
value (a sorted list of NodeShape), so this is a reading region: the oracle
is equality of what both versions produce from the same input graph
(fixture.ttl), not graph isomorphism. The entry point takes ``self`` rather
than a graph, so a fake ``self`` is built per call from the fixture instead
of using ``fixture=`` directly.
"""
from pathlib import Path

from rdfeval.harness import fixture_graph, run_pair
from shim import SHAPE_QUERY

FIXTURE = "fixture.ttl"


class _FakeProperty:
    """Stand-in for a ShaclProperty instance: only .iri, .graph, .SHAPE_QUERY
    are read by the region. Compared by .iri only -- the fresh fixture graph
    parsed for each side gets its own blank-node-derived identifier, which is
    not part of what the region is expected to preserve."""

    def __init__(self, iri, graph, shape_query):
        self.iri = iri
        self.graph = graph
        self.SHAPE_QUERY = shape_query

    def __eq__(self, other):
        return isinstance(other, _FakeProperty) and self.iri == other.iri

    def __repr__(self):
        return f"_FakeProperty({self.iri!r})"


def _case(iri):
    def make():
        graph = fixture_graph(Path(__file__).parent / FIXTURE)
        return (_FakeProperty(iri, graph, SHAPE_QUERY),), {}
    return make


VERDICT = run_pair(
    __file__,
    entry="get_nodeshapes",
    calls=[
        _case("http://example.org/prop1"),  # two matching shapes
        _case("http://example.org/prop2"),  # zero solutions
        _case("http://example.org/otherProp"),  # exactly one matching shape
    ],
    ordered=True,  # the region itself sorts by label
)

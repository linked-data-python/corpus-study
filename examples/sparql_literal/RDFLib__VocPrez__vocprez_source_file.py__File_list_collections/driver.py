"""Validation driver for RDFLib__VocPrez__vocprez_source_file.py__File_list_collections.

`list_collections` is a reading region (design record corpus/405): its whole
effect is a SELECT projected into a list of (concept, label) pairs, so the
oracle is value equality against a fixture graph, not graph isomorphism.

`self` is restored (AGENT_BATCH's ~163-regions case: the graph is reached
through `self.gr`, a binding the line-range extraction cannot carry) as a
bare stand-in exposing only the `.gr` attribute this region actually reads
-- nothing else of the real `File` class is needed or invented.

`fixture.ttl` is parsed fresh for each call. `_call()` matches two real
skos:Concept/rdfs:label pairs, plus neighbouring triples that must NOT
appear: a skos:Concept with no rdfs:label, and an rdfs:label on a resource
that is not a skos:Concept. `_call_empty()` is the zero-solution case, a
graph with no skos:Concept at all. `SELECT *` has no `ORDER BY`, so the
result order is unspecified: `ordered=False`.

`run_pair` also compares the arguments a call was made with (so a region
that MUTATES its input is caught even if it returns nothing) -- but
`rdflib.Graph.__eq__` compares by `.identifier`, a random blank node unless
given one, not by content (verified directly: two graphs parsed from
identical Turtle do not compare equal). `list_collections` never mutates
`self.gr`, so that comparison would only ever be reporting on two fresh
`Graph()` objects' random identifiers, never on the region itself; `_Self`
below says so explicitly (`__eq__` always agrees) instead of leaving an
accidental, unexplained bnode mismatch for a reviewer to chase.
"""
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import run_pair, fixture_graph

_FIXTURE = Path(__file__).parent / "fixture.ttl"


class _Self:
    """Stand-in for the real `File` instance: carries only `.gr`, the one
    attribute this region reads. Never mutated by the call, so its
    identity is not an observable of the comparison -- the proof is the
    RETURN value, materialised and compared for real below."""

    def __init__(self, gr):
        self.gr = gr

    def __eq__(self, other):
        return True


def _call():
    return (_Self(gr=fixture_graph(_FIXTURE)),), {}


def _call_empty():
    return (_Self(gr=Graph()),), {}


VERDICT = run_pair(
    __file__,
    entry="list_collections",
    fixture="fixture.ttl",
    calls=[_call, _call_empty],
    ordered=False,
)

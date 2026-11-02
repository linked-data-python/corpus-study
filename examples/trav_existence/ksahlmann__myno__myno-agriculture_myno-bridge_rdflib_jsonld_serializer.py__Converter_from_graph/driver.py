"""Validation driver for ksahlmann__myno__myno-agriculture_myno-bridge_rdflib_jsonld_serializer.py__Converter_from_graph.

The region is a method of the JSON-LD `Converter`; its `self` only has to
offer `process_subject(graph, s, nodemap)`.  A recorder stands in for it (a
stub in the driver, identical on both sides): it logs each subject it is
handed and stores a node object under it in `nodemap`, so what the region
returns (`list(nodemap.values())`) and what it dispatched (`self.seen`) are
both compared.  Which subjects it dispatches is exactly what the read
decides: every IRI subject, and a blank-node subject only when nothing
points at it (`not any(graph.subjects(None, s))`).

fixture.ttl is parsed fresh for each side.  Calls: the fixture (IRIs,
unreferenced bnodes, bnodes referenced by an IRI / by a bnode / through a
cycle / in an rdf:type position), and an empty graph (zero solutions).
Solutions of a set() come in an unspecified order: compared as multisets.
"""
from rdflib import Graph

from rdfeval.harness import run_pair, fixture_graph
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"


class Recorder:
    """Stand-in for the Converter instance."""

    def __init__(self):
        self.seen = []

    def process_subject(self, graph, s, nodemap):
        self.seen.append(s)
        nodemap[s] = {"@id": s, "triples": len(list(graph.predicate_objects(s)))}


VERDICT = run_pair(
    __file__,
    entry='from_graph',
    fixture="fixture.ttl",
    calls=[
        lambda: ((Recorder(), fixture_graph(FIXTURE)), {}),
        lambda: ((Recorder(), Graph()), {}),
    ],
)

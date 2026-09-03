"""Validation driver for Omegaice__pydantic-rdf__tests_test_deserialize.py__test_property_paths.

Establishes semantic equivalence of original.py and translated.ldpy.

test_property_paths(graph, EX) takes `graph` as an argument and mutates it
in place; run_pair compares call arguments after the call returns, so the
oracle is isomorphism on that mutated graph (meta.json's "oracle":
"isomorphism") -- settled by the region's own `graph.add()`/`+{ }` lines,
before Organization.parse_graph(graph, org) (stubbed, see context_shim.py)
is ever reached.
"""
from rdflib import Graph, Namespace

from rdfeval.harness import run_pair


def _fixture():
    # Mirrors the real `graph`/`EX` pytest fixtures in
    # Omegaice/pydantic-rdf@8f145956d8 : tests/conftest.py -- a fresh Graph
    # bound to "ex", and EX = Namespace("http://example.com/"). Called once
    # per side (run_pair invokes this once per call, per side) so each
    # version mutates its own fresh graph.
    ex = Namespace("http://example.com/")
    g = Graph()
    g.bind("ex", ex)
    return (g, ex), {}


VERDICT = run_pair(
    __file__,
    entry="test_property_paths",
    calls=[_fixture],
)

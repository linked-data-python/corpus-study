"""Validation driver for boricles__ontosphere__backend_app_api_import_rdf.py___label_for.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

`_label_for(g, subject, uri_str)` takes three arguments, not just a graph,
so the calls are written by hand instead of using the generic fixture=
wiring (which passes a lone parsed Graph as the sole argument).
"""
from pathlib import Path

from rdflib import Graph, URIRef

from rdfeval.harness import run_pair

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
EX = "http://example.org/"


def _graph():
    g = Graph()
    g.parse(FIXTURE, format="turtle")
    return g


def _case_has_label():
    uri = EX + "withLabel"
    return ((_graph(), URIRef(uri), uri), {})


def _case_no_label():
    # Zero-solution case: falls back to the fragment after '/' or '#'.
    uri = EX + "withoutLabel"
    return ((_graph(), URIRef(uri), uri), {})


VERDICT = run_pair(
    __file__,
    entry='_label_for',
    calls=[_case_has_label, _case_no_label],
)

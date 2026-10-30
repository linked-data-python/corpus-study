"""Validation driver for boricles__ontosphere__backend_app_api_import_rdf.py___label_for.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

`_label_for(g, subject, uri_str)` takes three arguments, not just a graph,
so the calls are written by hand instead of using the generic fixture=
wiring (which passes a lone parsed Graph as the sole argument).

The repository's three call sites (backend/app/api/import_rdf.py:142, 162,
233) pass a URIRef subject (blank nodes are skipped before the call) and
``str(subj)`` as ``uri_str``; every case below does the same.

Repair of 2026-10-30 -- one subject per way the read can decide the result:
the falsy labels ``""``, ``0`` and ``"false"^^xsd:boolean`` (the ``if val:``
guard falls back to the fragment; ``if val is not None`` would not), two
labels whose first stored value is ``""`` and then text (``graph.value``
keeps the first, so the guard still falls back; another pick would not),
the same in the other order, a ``@fr`` label, an IRI label, and two
unlabelled URIs ending in a ``#`` fragment and in ``/``.
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


def _case(local):
    uri = local if local.startswith("http") else EX + local
    return lambda: ((_graph(), URIRef(uri), uri), {})


_REPAIR_CASES = [
    _case(n) for n in (
        "emptyLabel", "zeroLabel", "falseLabel", "emptyThenText",
        "textThenEmpty", "frenchLabel", "iriLabel",
        "http://example.org/ns#hashFragment", "http://example.org/trailing/",
    )
]

VERDICT = run_pair(
    __file__,
    entry='_label_for',
    calls=[_case_has_label, _case_no_label] + _REPAIR_CASES,
)

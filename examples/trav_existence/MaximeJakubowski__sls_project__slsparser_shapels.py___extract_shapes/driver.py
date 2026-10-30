"""Validation driver for MaximeJakubowski__sls_project__slsparser_shapels.py___extract_shapes.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  Each fixture is parsed fresh for each side.

The fixture is part of the translation: it must hold several solutions of the
pattern the region reads, the zero-solution case, and neighbouring triples
that must NOT match.

Three calls:

* `fixture.ttl`: one shape per branch of the union (object parameter,
  subject parameter, rdf:type, sh:or member) and neighbours that must not
  match (untracked sh:severity/sh:message, a list member with sh:path, a
  node typed with another class).
* `fixture_params.ttl` (added 2026-10-30, after triage): EVERY predicate of
  `object_parameters` (4) and `subject_parameters` (30) gives a shape
  reachable only through it, so a typo or a dropped entry in either list is
  a set difference; the objects of the subject-only parameters (IRIs,
  literals, a list) must not become shapes. It also covers sh:and and sh:xone
  (fixture.ttl has only sh:or), blank-node and literal list members, a member
  with sh:path in each list, and an empty list.
* an empty graph: the zero-solution case for every read (empty set).
"""
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import fixture_graph, run_pair

_EX_DIR = Path(__file__).resolve().parent

VERDICT = run_pair(
    __file__,
    entry='_extract_shapes',
    fixture="fixture.ttl",
    calls=[
        lambda: ((fixture_graph(_EX_DIR / "fixture.ttl"),), {}),
        lambda: ((fixture_graph(_EX_DIR / "fixture_params.ttl"),), {}),
        lambda: ((Graph(),), {}),
    ],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)

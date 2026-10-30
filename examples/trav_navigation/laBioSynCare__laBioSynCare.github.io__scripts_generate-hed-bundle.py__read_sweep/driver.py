"""Validation driver for laBioSynCare__laBioSynCare.github.io__scripts_generate-hed-bundle.py__read_sweep.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  Each fixture is parsed fresh for each side.

read_sweep returns the FIRST qualifying track only, so one graph shows one
outcome: the driver makes one call per fixture, each aimed at one behaviour.

- ``fixture.ttl``: one sweep among neighbours that must not be returned (flat,
  incomplete, unrelated, no initial period).  The sweep carries other
  properties of the same subject before the three the region reads, as in the
  repository's data: a read whose predicate is widened to a variable gets one
  of them first.
- ``fixture_multivalued.ttl``: multi-valued predicates.  The original reads the
  first value of each (``next(..., None)``); a three-pattern join reaches the
  other combinations, and ``.one()`` raises.  This is the case that showed
  the first translation (one conjunctive m{ }) wrong.
- ``fixture_order.ttl``: two sweeps, met in an order that differs from the
  order written, and an incomplete track met first (kills a dropped guard).
- an empty graph: the zero-solution case, None on both sides.

The repository calls read_sweep on a Graph parsed from a Turtle bundle
(scripts/generate-hed-bundle.py:432-439 and :667), which is what every call
passes.
"""
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import run_pair, fixture_graph

HERE = Path(__file__).resolve().parent

VERDICT = run_pair(
    __file__,
    entry='read_sweep',
    fixture="fixture.ttl",
    calls=[
        lambda: ((fixture_graph(HERE / "fixture.ttl"),), {}),
        lambda: ((fixture_graph(HERE / "fixture_multivalued.ttl"),), {}),
        lambda: ((fixture_graph(HERE / "fixture_order.ttl"),), {}),
        lambda: ((Graph(),), {}),
    ],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)

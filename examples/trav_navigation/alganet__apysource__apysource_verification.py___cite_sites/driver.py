"""Validation driver for alganet__apysource__apysource_verification.py___cite_sites.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

`_cite_sites(g, urn)` takes two arguments, so the generic ``fixture=`` wiring
(a single positional graph argument) does not apply directly: `calls`
supplies the graph plus each `urn` to exercise -- a urn with three citing
sites (one complete, one file-only, one skipped for missing citingFile,
plus neighbouring data under a different urn that must not leak in), a urn
present in the graph but with no citing sites at all (the zero-solution
case), and the empty-string urn, which the region's own `if not urn: return
[]` must short-circuit before ever touching the graph.

Added by the 2026-10-31 mutation audit: `ex:doc_falsy`, cited from blank
nodes (as yaml_input.py mints them), with a site whose file is "" and line 0,
a site with line 0, a site with two sv:citingLine values and one with two
sv:citingFile values.  It kills the truthiness rewrites `if not file` (drops
the "" site) and `if line` (turns line 0 into None), and the join that absorbs
the citingFile `g.value()` into the citedBy loop (two CiteSites instead of
one), all of which the first three calls left alive.
"""
from pathlib import Path

from rdfeval.harness import run_pair, fixture_graph

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"


def _case(urn):
    return lambda: ((fixture_graph(FIXTURE), urn), {})


VERDICT = run_pair(
    __file__,
    entry='_cite_sites',
    fixture="fixture.ttl",
    calls=[
        _case("http://example.org/doc1"),
        _case("http://example.org/doc_no_sites"),
        _case(""),
        _case("http://example.org/doc_falsy"),
    ],
    ordered=True,  # the region itself does `sorted(sites, key=...)`
)

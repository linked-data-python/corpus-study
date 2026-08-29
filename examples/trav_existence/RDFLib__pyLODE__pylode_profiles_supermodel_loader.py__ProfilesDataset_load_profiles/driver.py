"""Validation driver for RDFLib__pyLODE__pylode_profiles_supermodel_loader.py__ProfilesDataset_load_profiles.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405). `fixture.ttl` holds three profiles: one whose resource fetches a
non-Profile artifact (the FALSE / zero-solution branch of
`new_graph.value(None, RDF.type, PROF.Profile)`), one whose resource fetches
an artifact that IS itself a Profile (the TRUE branch, recursing into
`load_profiles`), and one whose resource declares a mediatype the region does
not know how to fetch (`MEDIA_TYPES` neighbourhood, never reaches `fetch`) --
plus a subject that looks like a profile but is not typed `prof:Profile`,
which `graph.subjects(RDF.type, PROF.Profile)` must not pick up.

`entry` is the `demo` harness both files carry identically (see meta.json):
the region is a method returning nothing -- its only observable effect is
what it hands to `self.add_graph`. `demo` runs it against a fresh `Loader`
(the context shim's ProfilesDataset stand-in, which replaces the real
httpx-backed `fetch` with a fixed lookup so the driver performs no network
I/O) and returns the graphs collected, sorted by identifier.

`ordered=True`: that sort, not the store, is what fixes the order of what
`demo` returns.
"""
from pathlib import Path

from rdflib import Graph as _Graph
from rdfeval.harness import run_pair, fixture_graph

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"


def case():
    graph = fixture_graph(FIXTURE)
    prev_graph = _Graph()  # unused by the region; only its signature needs it
    return (graph, prev_graph), {}


VERDICT = run_pair(
    __file__,
    entry="demo",
    fixture="fixture.ttl",
    ordered=True,
    calls=[case],
)

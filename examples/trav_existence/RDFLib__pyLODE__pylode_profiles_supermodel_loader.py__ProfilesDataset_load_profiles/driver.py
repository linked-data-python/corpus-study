"""Validation driver for RDFLib__pyLODE__pylode_profiles_supermodel_loader.py__ProfilesDataset_load_profiles.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405). `fixture.ttl` holds four profiles: one whose resource fetches a
non-Profile artifact (the FALSE / zero-solution branch of
`new_graph.value(None, RDF.type, PROF.Profile)`), one whose resource fetches
an artifact that IS itself a Profile (the TRUE branch, recursing into
`load_profiles`), and one whose resource declares a mediatype the region does
not know how to fetch (`MEDIA_TYPES` neighbourhood, never reaches `fetch`) --
plus a subject that looks like a profile but is not typed `prof:Profile`,
which `graph.subjects(RDF.type, PROF.Profile)` must not pick up.

The fourth, ex:profileD (repair of 2026-10-31), carries three descriptors
in one profile_graph: a `lode:config` one (the `role == LODE.config` branch,
with its own recursion into the lode:Module profile its artifact declares),
one with no `prof:hasRole` (value() gives None: `.one()` / `next(iter())`
would raise), and one with an unfetchable format.  Three distinct roles,
formats and artifacts in one graph: a `.first()` whose subject is widened
gives all three the same value, and at least one goes wrong.

`entry` is the `demo` harness both files carry identically (see meta.json):
the region is a method returning nothing -- its only observable effect is
what it hands to `self.add_graph`. `demo` runs it against a fresh `Loader`
(the context shim's ProfilesDataset stand-in, which replaces the real
httpx-backed `fetch` with a fixed lookup so the driver performs no network
I/O) and returns the graphs collected, sorted by identifier.

Two seams added here, identical for both sides (repair of 2026-10-31):

  * the config graph.  The real `ProfilesDataset.__init__` add_graph()s the
    `urn:graph:pylode-config` graph before calling load_profiles
    (loader.py:165), so what the config branch parses into it is part of the
    dataset.  The driver makes each fresh Loader do the same, so `demo`
    returns it among the graphs; the canned config artifact (`pylode.ttl`,
    shaped as in supermodel.md:95-106) is added to the shim's lookup here.
  * the `logging` journal.  The repository logs at DEBUG
    (loader.py:11) a message carrying each `remote_resource` the region
    fetches; run_pair compares the region's log records itself.

`ordered=True`: that sort, not the store, is what fixes the order of what
`demo` returns.

Mutants killed (each in a copy of the pair): either outer pattern widened or
emptied, resource island emptied, existence forced True / False or widened,
mediatype set to None (before this repair); role set to None, role `.one()`
and `next(iter())`, subject of each of the three `.first()` widened to `[]`
(by ex:profileD).  Equivalent, not counted: the resource loop read on
`graph` instead of `profile_graph` (foreign descriptors have no
format/role/artifact in profile_graph: str(None) is not a media type).
"""
import contextlib
import io
import logging
import sys
from collections import Counter
from pathlib import Path

from rdflib import Graph as _Graph, URIRef as _URIRef
from rdfeval import harness
from rdfeval.harness import run_pair, fixture_graph

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import context_shim  # noqa: E402 - the very module both sides import

context_shim._REMOTE["http://example.org/artifacts/pylode.ttl"] = (
    "@prefix ex: <http://example.org/> .\n"
    "@prefix prof: <http://www.w3.org/ns/dx/prof/> .\n"
    "@prefix lode: <https://w3id.org/lode/ns/pylode/> .\n"
    "@prefix sh: <http://www.w3.org/ns/shacl#> .\n"
    "ex:geometryprim a prof:Profile , lode:Module ; sh:order 1 .\n",
    "text/turtle",
)

_init = context_shim.Loader.__init__


def _init_with_config(self):
    _init(self)
    # loader.py:165 -- the config graph is in the dataset from the start
    self.add_graph(self.get_graph(_URIRef("urn:graph:pylode-config")))


context_shim.Loader.__init__ = _init_with_config


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

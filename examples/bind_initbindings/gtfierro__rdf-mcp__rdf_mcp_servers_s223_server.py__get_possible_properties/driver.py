"""Validation driver for gtfierro__rdf-mcp__rdf_mcp_servers_s223_server.py__get_possible_properties.

HERMETIC. Both original.py and translated.ldpy run, at module level,
`ontology = Graph().parse("https://open223.info/223p.ttl")`, a live fetch of a
third-party file. This driver intercepts exactly that URL -- `Graph.parse` is
wrapped before the two modules are executed, and the URL is answered with the
local `ontology_fixture.ttl` (a miniature of the 223P ontology, comments in
the file) -- so the verdict no longer depends on the network or on the
current content of the live ontology. Any other URL passed to `Graph.parse`
raises, so the interception cannot hide a second fetch. The region itself
(original.py, translated.ldpy) is untouched. Set `RDFEVAL_LIVE_223P=1` to
bypass the interception and run against the real ontology, as the first
version of this driver did.

The query reads, for a class `?from`: every class `?fromp` on its
`rdfs:subClassOf*` chain (itself included), then the node shapes of
`?fromp` through a UNION of two branches -- (1) a shape with
`sh:targetClass ?fromp`, (2) `?fromp` being itself an `sh:NodeShape` -- and
the non-blank `sh:path`s of their `sh:property`. Calls (the result is a set
turned into a list, so it is compared as a multiset: `ordered=False`):

* "Zone" and "NoSuchClass223Term" -- the two calls of the first version
  (against the live ontology: five paths, and zero). Here "Zone" walks a
  three-level chain, so it collects paths from BOTH branches at several
  levels: Root's targeting shape (branch 1, two hops up), Concept as its own
  shape (branch 2, one hop up), Zone's own targeting shape and Zone as its
  own shape; a blank-node path is dropped by `FILTER (!isBlank(?path))`; a
  path stated by both Zone shapes is counted once (the `set`); paths of the
  SUBCLASS SubZone and of the sibling-branch Pump are not returned;
* "SubZone" -- the same chain one step lower, to add its own path and keep
  the inherited ones;
* "Sensor" -- branch 1 ONLY: a targeting shape, no node-shape class, no
  parent. Making branch 1 dead (`FILTER(1 = 2)` inside it) makes this
  call fail, together with "Zone", "SubZone" and "Root";
* "Connection" -- branch 2 ONLY: the class is its own node shape and no
  shape targets it. Making branch 2 dead (`FILTER(1 = 2)` inside it) makes this call
  fail, together with "Zone" and "SubZone";
* "Bare" and "Empty" -- a class with no shape, and a targeting shape with no
  `sh:property`: zero paths, but through existing nodes rather than an
  unknown term;
* "Root" -- the top of the chain: only its own shape's path, none of its
  descendants' (the walk goes UP the subclass chain, not down);
* "" -- the empty string, `S223[""]` being the bare namespace IRI, a node of
  no class: zero paths.
"""
import os
from pathlib import Path

import rdflib
from rdfeval.harness import run_pair

ONTOLOGY_URL = "https://open223.info/223p.ttl"
FIXTURE = Path(__file__).resolve().parent / "ontology_fixture.ttl"

if not os.environ.get("RDFEVAL_LIVE_223P"):
    _real_parse = rdflib.Graph.parse

    def _parse(self, source=None, *args, **kwargs):
        if source != ONTOLOGY_URL:
            raise RuntimeError(f"unexpected Graph.parse({source!r}): the driver "
                               f"only stands in for {ONTOLOGY_URL}")
        return _real_parse(self, source=str(FIXTURE), format="turtle")

    rdflib.Graph.parse = _parse

VERDICT = run_pair(
    __file__,
    entry='get_possible_properties',
    calls=[
        (("Zone",), {}),
        (("NoSuchClass223Term",), {}),
        (("SubZone",), {}),
        (("Sensor",), {}),
        (("Connection",), {}),
        (("Bare",), {}),
        (("Empty",), {}),
        (("Root",), {}),
        (("",), {}),
    ],
    ordered=False,
)

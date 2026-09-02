"""Validation driver for BrickSchema__Brick__tools_compare_versions_compare_versions.py__get_tag_sets.

This region READS a graph via a SPARQL SELECT with a transitive property
path (`rdfs:subClassOf+`) and a root class interpolated in term position, so
the oracle is the equality of the values both versions produce from the same
input graph (design record corpus/405).  `fixture.ttl` is parsed fresh for
each call.

The original closes over a module-level `g` (always empty) rather than
taking a graph parameter; `graph=g` was added identically to both
representations (see original.py) to restore that binding, per
AGENT_BATCH.md's note on the ~163 regions with no visible graph parameter.
`calls=` therefore supplies `root` positionally and the fixture graph as the
`graph` keyword, once per root class:

  - brick:Sensor       -> several solutions (a two-hop subclass chain)
  - brick:Luminance_Sensor -> the zero-solution case (present in no triple)
"""
from pathlib import Path

from rdflib import Namespace

from rdfeval.harness import run_pair, fixture_graph

BRICK = Namespace("https://brickschema.org/schema/Brick#")

_FIXTURE = Path(__file__).parent / "fixture.ttl"


def _call(root):
    def build():
        return (root,), {"graph": fixture_graph(_FIXTURE)}
    return build


VERDICT = run_pair(
    __file__,
    entry="get_tag_sets",
    calls=[
        _call(BRICK.Sensor),
        _call(BRICK.Luminance_Sensor),
    ],
)

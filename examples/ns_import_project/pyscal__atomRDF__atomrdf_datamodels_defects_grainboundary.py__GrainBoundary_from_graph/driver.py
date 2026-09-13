"""Validation driver for pyscal__atomRDF__atomrdf_datamodels_defects_grainboundary.py__GrainBoundary_from_graph.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

`demo(graph, sample)` (identical on both sides, appended after the extracted
region -- see meta.json) attaches `from_graph` to the shim's GrainBoundary
class and calls it through the ordinary classmethod protocol, returning a
plain dict (a pydantic model instance would compare unequal across the two
exec'd modules' distinct classes).

Two calls: (1) ex:sample1 -- two defects on the material, one a
TwistGrainBoundary neighbour that must not match and one a GrainBoundary
with full property data; (2) ex:sample2 -- a material with a defect, but
none of the right type -- the zero-solution branch reached through a
non-empty for-loop.
"""
from pathlib import Path

from rdflib import Namespace

from rdfeval.harness import fixture_graph, run_pair

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"

EX = Namespace("http://example.org/")


def call_grain_boundary_found():
    return ((fixture_graph(FIXTURE), EX.sample1), {})


def call_zero_solutions():
    return ((fixture_graph(FIXTURE), EX.sample2), {})


VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[call_grain_boundary_found, call_zero_solutions],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)

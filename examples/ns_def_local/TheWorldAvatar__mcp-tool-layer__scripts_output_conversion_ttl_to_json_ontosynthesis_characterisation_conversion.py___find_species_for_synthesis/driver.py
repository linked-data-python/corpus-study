"""Validation driver for TheWorldAvatar__mcp-tool-layer__scripts_output_conversion_ttl_to_json_ontosynthesis_characterisation_conversion.py___find_species_for_synthesis.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

The region takes a second argument (`synth`, the URIRef whose species are
looked up), so `calls=` supplies one call per case covered by the fixture:
the direct-hit path, the label-matching fallback path, and the
zero-solution path.
"""
from pathlib import Path

from rdflib import URIRef

from rdfeval.harness import run_pair, fixture_graph

FIXTURE = Path(__file__).parent / "fixture.ttl"

SYNTH_DIRECT = URIRef("http://example.org/synth/direct")
SYNTH_FALLBACK = URIRef("http://example.org/synth/fallback")
SYNTH_NONE = URIRef("http://example.org/synth/none")

VERDICT = run_pair(
    __file__,
    entry="_find_species_for_synthesis",
    calls=[
        lambda: ((fixture_graph(FIXTURE), SYNTH_DIRECT), {}),
        lambda: ((fixture_graph(FIXTURE), SYNTH_FALLBACK), {}),
        lambda: ((fixture_graph(FIXTURE), SYNTH_NONE), {}),
    ],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)

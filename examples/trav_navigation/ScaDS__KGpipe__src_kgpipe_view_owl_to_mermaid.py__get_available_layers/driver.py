"""Validation driver for ScaDS__KGpipe__src_kgpipe_view_owl_to_mermaid.py__get_available_layers.

Establishes semantic equivalence of original.py and translated.ldpy.

get_available_layers(ttl_path) parses its own graph from a path, so the
generic ``fixture=`` wiring (which parses a graph and passes it as the sole
argument) does not apply here: the fixture path itself is the argument.
"""
from pathlib import Path
from rdfeval.harness import run_pair

_FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"

VERDICT = run_pair(
    __file__,
    entry='get_available_layers',
    calls=[lambda: ((_FIXTURE,), {})],
    ordered=True,  # the region itself does `sorted(layer_names)`
)

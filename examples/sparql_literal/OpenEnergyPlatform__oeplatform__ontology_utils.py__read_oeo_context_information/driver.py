"""Validation driver for OpenEnergyPlatform__oeplatform__ontology_utils.py__read_oeo_context_information.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

The region does not take a graph directly: it takes `path` and `file`, joins
them, and parses the result itself (`g.parse(Ontology_URI.as_posix())`), so
the usual `fixture=` shortcut (which hands a pre-parsed Graph as the single
argument) does not fit this signature. `calls=` passes `(path, file)`
pointing at fixture.ttl instead, and reads it fresh on each side because
`g.parse` opens the file itself every call.

Two calls exercise both branches of `if ontology in [OPEN_ENERGY_ONTOLOGY_NAME]`:
one with `ontology="oeo"` (all five queries run, including the two obo:
queries), one with `ontology=None` (only the first three run, and
classes_definitions/classes_notes fall back to empty dicts).
"""
from pathlib import Path

from rdfeval.harness import run_pair

_EX_DIR = Path(__file__).resolve().parent

VERDICT = run_pair(
    __file__,
    entry='read_oeo_context_information',
    calls=[
        lambda: ((_EX_DIR, "fixture.ttl"), {"ontology": "oeo"}),
        lambda: ((_EX_DIR, "fixture.ttl"), {"ontology": None}),
    ],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)

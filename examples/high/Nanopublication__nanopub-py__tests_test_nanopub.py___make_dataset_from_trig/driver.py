"""Validation driver: _make_dataset_from_trig parses a TriG test file.

The region returns a Dataset, which the harness cannot compare directly
(rdflib.compare.to_isomorphic ingests triples, a Dataset yields quads), so
both files end with an identical small demo harness that calls the region
and flattens the result into a module-level Graph.  The driver therefore
compares module state: `demo_union` on each side, plus stdout.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__)

"""Validation driver: _minimal_valid_nanopub returns a Nanopub object.

A Nanopub is not comparable by the harness, so both files end with an
identical demo harness (see meta.json) that calls the helper once and binds
its three named graphs (assertion, provenance, pubinfo) to module-level
variables; module-state comparison then checks the three graphs by
isomorphism plus the printed ``is_valid`` verdict.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__)

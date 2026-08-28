"""Validation driver: AllClasses is a generator, so module state is compared.

Both files end with an identical demo harness (see meta.json) that consumes
the generator over a small OWL graph; the harness then compares the demo
graph and the printed class list.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__)

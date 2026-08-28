"""Validation driver: the region is a module of namespace declarations.

There is no graph and no entry point, so both files end with an identical
demo harness (see meta.json) printing the name -> IRI table the module
defines; the harness compares the captured stdout.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__)

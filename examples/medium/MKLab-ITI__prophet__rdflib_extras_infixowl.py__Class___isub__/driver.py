"""Validation driver: the region is Class.__isub__, an in-place operator.

It mutates the graph behind ``self`` and returns ``self``, an infixowl Class
that the harness cannot compare, so both files end with an identical demo
harness (see meta.json) building a three-class hierarchy and retracting one
rdfs:subClassOf edge through the operator.  Module state comparison then covers
the resulting graph and the printed list of remaining subclasses.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__)

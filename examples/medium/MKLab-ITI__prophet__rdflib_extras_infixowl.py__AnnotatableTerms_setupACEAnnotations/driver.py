"""Validation driver: the region is a method of AnnotatableTerms.

It only mutates ``self`` (six Property wrappers) and the graph behind it, so
both files end with an identical demo harness (see meta.json) that attaches the
method to a tiny object over a fresh graph.  Module state comparison then
covers the resulting graph, the six property identifiers and the 'ace' prefix
binding the method installs.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__)

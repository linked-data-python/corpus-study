"""Validation driver for chin-rcip__CRITERIA__criteria.py__shapeProc.

This region READS two graphs (dataGraph, plus the shape graph it parses
itself from a path given by shapeInput) and mutates the module-level
nodeLabels/nodeLink dicts rather than returning a value, so an entry=/
fixture= call would observe nothing (shapeProc's return is None and its
argument dataGraph is only read, never mutated). Instead, both original.py
and translated.ldpy call shapeProc themselves against fixture.ttl (dataGraph)
and shape.ttl (the shape graph, parsed by the region itself) and print the
resulting nodeLabels/nodeLink, sorted, so entry=None module-state comparison
sees it via stdout.

fixture.ttl / shape.ttl are part of the translation: together they hold
several solutions of the patterns the region reads, propShapes missing one
of the optional predicates, and neighbouring triples that must NOT match.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)

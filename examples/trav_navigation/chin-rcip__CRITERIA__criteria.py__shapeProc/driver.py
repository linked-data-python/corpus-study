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

The 2026-10-30 repair enriched both files (the call itself is in the
driving code of the two artefacts, which it leaves unchanged):

- ex:PlaceShape is the shape the repository really writes
  (rdf/demo_shape.shacl): anonymous property shapes, one with a
  sh:defaultValue labelled in dataGraph, one with an empty sh:description
  (``if nodeURL:`` is false on "", ``if True:`` would add a nodeLink key);
- ex:NotAShape2 (typed sh:PropertyShape) and ex:NotAShape3 (``rdfs:seeAlso
  sh:NodeShape``) have skos:example AND a sh:property, so the NodeShape guard
  is observable: replacing it with ``True``, or widening its rdf:type or
  sh:NodeShape to a variable, adds their labels;
- one neighbour per bound predicate (rdfs:seeAlso for skos:example,
  sh:targetClass beside sh:property, rdfs:comment beside sh:path/sh:name/
  sh:description, skos:note beside rdfs:label in dataGraph) kills the mutants
  that widen that predicate to a variable.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)

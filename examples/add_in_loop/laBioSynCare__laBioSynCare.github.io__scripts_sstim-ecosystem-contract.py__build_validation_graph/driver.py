"""Validation driver for laBioSynCare__laBioSynCare.github.io__scripts_sstim-ecosystem-contract.py__build_validation_graph.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side; the catalog the
region loads itself is `ontology/instances/implementations/implementations.ttl`.

The fixture is part of the translation: it must hold several solutions of the
pattern the region reads, the zero-solution case, and neighbouring triples
that must NOT match.  Here:

* call 0 (fixture.ttl): targets A, C, E retained (A reached twice); B (wrong
  type) and Z (absent from the catalog) skipped; D (reached through another
  predicate) left out; the catalog holds, for the retained targets A and C,
  predicates OUTSIDE the closed profile (ex:protocol, rdfs:comment,
  dcterms:title) and a second rdfs:label, so a profile widened to
  "every predicate of the target" is a different graph;
* call 1: an empty artifact (zero solutions): the result is the context alone;
* call 2: an artifact that already holds one of the profile triples it would
  receive (rdf:type of A), plus a target that is a literal, which no catalog
  node can match, plus a target (targetC) reached from a node that is itself a catalog node, and
  targetF, a target that only the edge-case artifact reaches;
* call 3: only the targets B and Z (nothing retained): the context plus the
  artifact's own triples.
"""
from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF
from rdfeval.harness import fixture_graph, run_pair

FIXTURE = Path(__file__).parent / "fixture.ttl"
EX = Namespace("http://example.org/")
ECO = Namespace("https://w3id.org/sstim/ecosystem#")
SSTIM = Namespace("https://w3id.org/sstim#")


def _empty():
    return (Graph(),), {}


def _edge_cases():
    g = Graph()
    g.add((EX.relX, ECO.relationshipTarget, Literal("targetA")))
    g.add((EX.targetA, RDF.type, SSTIM.SensoryStimulationImplementation))
    g.add((EX.targetA, ECO.relationshipTarget, EX.targetC))
    g.add((EX.relY, ECO.relationshipTarget, EX.targetF))
    return (g,), {}


def _none_retained():
    g = Graph()
    g.add((EX.rel2, ECO.relationshipTarget, EX.targetB))
    g.add((EX.rel7, ECO.relationshipTarget, EX.targetZ))
    return (g,), {}


VERDICT = run_pair(
    __file__,
    entry='build_validation_graph',
    fixture="fixture.ttl",
    calls=[
        lambda: ((fixture_graph(FIXTURE),), {}),
        _empty,
        _edge_cases,
        _none_retained,
    ],
)

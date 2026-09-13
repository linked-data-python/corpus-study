"""Validation driver for hidden-graph__rdflib-starlight__starlight_query_evaluate_patches.py___decode_tt_hash.

This region READS a graph, so the oracle is the equality of the values both
versions produce from the same input graph (design record corpus/405), not
isomorphism -- despite the stratum's default. `calls=` builds a graph per
case, covering: a tt:HASH node with full encoding triples (several
components), a tt:HASH node missing one encoding triple (zero-solution case
for one of the three `.value()` reads), and a node that is not a tt:HASH URI
at all (neighbourhood that must not match).
"""
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF
from shim_encoding import TT_NS

from rdfeval.harness import run_pair

EX = "http://example.org/"


def _case_full():
    g = Graph()
    node = URIRef(TT_NS + "HASH-abc123")
    g.add((node, RDF.subject, URIRef(EX + "s1")))
    g.add((node, RDF.predicate, URIRef(EX + "p1")))
    g.add((node, RDF.object, Literal("o1")))
    # neighbourhood that must not match: another tt:HASH node's own triples
    other = URIRef(TT_NS + "HASH-other")
    g.add((other, RDF.subject, URIRef(EX + "s2")))
    g.add((other, RDF.predicate, URIRef(EX + "p2")))
    g.add((other, RDF.object, URIRef(EX + "o2")))
    return ((g, node), {})


def _case_missing():
    g = Graph()
    node = URIRef(TT_NS + "HASH-partial")
    g.add((node, RDF.subject, URIRef(EX + "s1")))
    g.add((node, RDF.predicate, URIRef(EX + "p1")))
    # no rdf:object triple -> zero-solution case -> function returns None
    return ((g, node), {})


def _case_not_tt():
    g = Graph()
    node = URIRef(EX + "plain-node")
    g.add((node, RDF.subject, URIRef(EX + "s1")))
    g.add((node, RDF.predicate, URIRef(EX + "p1")))
    g.add((node, RDF.object, URIRef(EX + "o1")))
    # node does not start with TT_NS -> isinstance/startswith guard rejects it
    return ((g, node), {})


VERDICT = run_pair(
    __file__,
    entry='_decode_tt_hash',
    calls=[_case_full, _case_missing, _case_not_tt],
)

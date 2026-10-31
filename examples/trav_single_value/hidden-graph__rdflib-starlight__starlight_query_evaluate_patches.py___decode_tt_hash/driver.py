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


# --- Repair audit (2026-10-31): cases the three calls above left open ---

def _case_decoy_first():
    # Another tt:HASH node's encoding triples stored BEFORE the right ones:
    # a subject widened to `[]` would pick them even through `.first()`.
    g = Graph()
    other = URIRef(TT_NS + "HASH-before")
    g.add((other, RDF.subject, URIRef(EX + "s-decoy")))
    g.add((other, RDF.predicate, URIRef(EX + "p-decoy")))
    g.add((other, RDF.object, URIRef(EX + "o-decoy")))
    node = URIRef(TT_NS + "HASH-after")
    g.add((node, RDF.subject, URIRef(EX + "s1")))
    g.add((node, RDF.predicate, URIRef(EX + "p1")))
    g.add((node, RDF.object, URIRef(EX + "o1")))
    return ((g, node), {})


def _case_missing_subject():
    # zero solutions for rdf:subject (the other two present)
    g = Graph()
    node = URIRef(TT_NS + "HASH-nosubject")
    g.add((node, RDF.predicate, URIRef(EX + "p1")))
    g.add((node, RDF.object, URIRef(EX + "o1")))
    return ((g, node), {})


def _case_missing_predicate():
    # zero solutions for rdf:predicate (the other two present)
    g = Graph()
    node = URIRef(TT_NS + "HASH-nopredicate")
    g.add((node, RDF.subject, URIRef(EX + "s1")))
    g.add((node, RDF.object, URIRef(EX + "o1")))
    return ((g, node), {})


def _case_two_values():
    # two solutions for each of the three reads: g.value keeps one,
    # `.one()` would raise
    g = Graph()
    node = URIRef(TT_NS + "HASH-two")
    for i in (1, 2):
        g.add((node, RDF.subject, URIRef(EX + f"s{i}")))
        g.add((node, RDF.predicate, URIRef(EX + f"p{i}")))
        g.add((node, RDF.object, URIRef(EX + f"o{i}")))
    return ((g, node), {})


def _case_falsy_object(obj):
    # a falsy literal object ("" or 0): `is None` keeps it, truthiness
    # would drop the triple term
    def case():
        g = Graph()
        node = URIRef(TT_NS + "HASH-falsy")
        g.add((node, RDF.subject, URIRef(EX + "s1")))
        g.add((node, RDF.predicate, URIRef(EX + "p1")))
        g.add((node, RDF.object, obj))
        return ((g, node), {})
    return case


VERDICT = run_pair(
    __file__,
    entry='_decode_tt_hash',
    calls=[_case_full, _case_missing, _case_not_tt,
           _case_decoy_first, _case_missing_subject, _case_missing_predicate,
           _case_two_values, _case_falsy_object(Literal("")),
           _case_falsy_object(Literal(0))],
)

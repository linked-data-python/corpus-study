"""Validation driver for Query.get_supermodel_iri.

The region is a method lifted out of pyLODE's ``Query``; it reads only
``self.graph`` and ``self.root_profile_iri``, so the fixtures pass a small
holder.  Three fixtures: one profile declared, several declared (the loop
keeps the last one, so a single-profile graph is the only deterministic
"found" case), and none declared (fallback to the root profile IRI).
"""
from rdflib import Graph, URIRef
from rdflib.namespace import PROF, RDF

from rdfeval.harness import run_pair, graphs_isomorphic

EX = "http://example.org/"
ROOT = URIRef(EX + "root-profile")


class Holder:
    """Stand-in for the pyLODE Query instance the method is bound to."""

    def __init__(self, graph):
        self.graph = graph
        self.root_profile_iri = ROOT

    def __eq__(self, other):
        return (self.root_profile_iri == other.root_profile_iri
                and graphs_isomorphic(self.graph, other.graph))

    def __repr__(self):
        return f"Holder({len(self.graph)} triples)"


def case_one_profile():
    g = Graph()
    g.add((URIRef(EX + "p1"), RDF.type, PROF.Profile))
    g.add((URIRef(EX + "p1"), RDF.type, URIRef(EX + "Other")))
    g.add((URIRef(EX + "x"), RDF.type, URIRef(EX + "Other")))
    return ((Holder(g),), {})


def case_no_profile():
    g = Graph()
    g.add((URIRef(EX + "x"), RDF.type, URIRef(EX + "Other")))
    return ((Holder(g),), {})


def case_empty_graph():
    return ((Holder(Graph()),), {})


VERDICT = run_pair(__file__, entry="get_supermodel_iri",
                   calls=[case_one_profile, case_no_profile,
                          case_empty_graph])

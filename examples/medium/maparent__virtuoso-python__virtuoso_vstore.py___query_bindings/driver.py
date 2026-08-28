"""Validation driver: _query_bindings maps a triple pattern to SPARQL
bindings.  It is a pure function, so the fixtures simply cover the branches:
wildcards (the four Variable defaults), a fully bound pattern, a Graph passed
for the context, blank nodes rewritten to Virtuoso nodeID:// IRIs, and the
to_n3=False variant that returns terms instead of their N3 form.

Blank nodes carry fixed labels so that _bnode_to_nodeid is deterministic and
the two runs stay comparable.
"""
from rdflib import Graph
from rdflib.term import BNode, Literal, URIRef

from rdfeval.harness import run_pair

EX = "http://example.com/"


def all_wildcards():
    return (((None, None, None),), {})


def fully_bound():
    return (((URIRef(EX + "s"), URIRef(EX + "p"), Literal("o", lang="en")),),
            {"g": URIRef(EX + "graph")})


def graph_context():
    return (((URIRef(EX + "s"), None, None),),
            {"g": Graph(identifier=URIRef(EX + "ctx"))})


def bnodes_no_n3():
    return (((BNode("b1"), URIRef(EX + "p"), BNode("abcdefghij")),),
            {"g": BNode("gctx"), "to_n3": False})


VERDICT = run_pair(__file__, entry="_query_bindings",
                   calls=[all_wildcards, fully_bound, graph_context,
                          bnodes_no_n3])

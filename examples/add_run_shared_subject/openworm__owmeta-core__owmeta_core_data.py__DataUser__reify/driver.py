"""Validation driver for openworm__owmeta-core__owmeta_core_data.py__DataUser__reify.

`_reify(self, g, s)` writes the four rdf:Statement triples of the triple `s`
into `g` and returns the statement node. Each call gets a fresh `g` that
already holds a neighbouring triple (which must survive), and a `self` from
context_shim.py. The calls cover an IRI object, a plain literal, a language
literal and a datatyped literal (the translation interpolates the object
as a term, so a literal must stay the literal it is), and a blank-node
subject. The harness compares the returned node, the mutated `g`, and `self`.
"""
from rdflib import BNode, Graph, Literal, URIRef, XSD

from rdfeval.harness import run_pair
from context_shim import DataUser

EX = "http://example.org/"


def _graph():
    g = Graph()
    g.add((URIRef(EX + "other"), URIRef(EX + "p"), Literal("kept")))
    return g


def _call(s):
    return lambda: ((DataUser(), _graph(), s), {})


VERDICT = run_pair(
    __file__,
    entry="_reify",
    calls=[
        _call((URIRef(EX + "a"), URIRef(EX + "knows"), URIRef(EX + "b"))),
        _call((URIRef(EX + "a"), URIRef(EX + "name"), Literal("Alice"))),
        _call((URIRef(EX + "a"), URIRef(EX + "label"), Literal("Alice", lang="en"))),
        _call((URIRef(EX + "a"), URIRef(EX + "age"), Literal("42", datatype=XSD.integer))),
        _call((BNode("x"), URIRef(EX + "knows"), URIRef(EX + "b"))),
    ],
)

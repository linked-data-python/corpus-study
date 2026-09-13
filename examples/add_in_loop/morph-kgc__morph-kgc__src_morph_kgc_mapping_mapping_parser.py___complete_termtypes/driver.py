"""Validation driver for morph-kgc__morph-kgc__src_morph_kgc_mapping_mapping_parser.py___complete_termtypes.

Establishes semantic equivalence of original.py and translated.ldpy.
"""
from rdflib import Graph, URIRef, Literal, BNode

from rdfeval.harness import run_pair
from rml_constants import (
    RML_QUOTED_TRIPLES_MAP, RML_TERM_TYPE, RML_RDF_STAR_TRIPLE,
    RML_CONSTANT, RML_BLANK_NODE, RML_LITERAL, RML_OBJECT_MAP,
    RML_REFERENCE, RML_PARENT_TRIPLES_MAP, RML_SUBJECT_MAP, RML_IRI,
)

EX = "http://example.org/"


def _make_graph():
    g = Graph()

    # branch 1: quoted triples map with no termtype -> gets RDFstarTriple
    tm1 = URIRef(EX + "tm1")
    g.add((tm1, URIRef(RML_QUOTED_TRIPLES_MAP), URIRef(EX + "qtm1")))

    # neighbour: already has a termtype -> must NOT be touched
    tm1b = URIRef(EX + "tm1b")
    g.add((tm1b, URIRef(RML_QUOTED_TRIPLES_MAP), URIRef(EX + "qtm1b")))
    g.add((tm1b, URIRef(RML_TERM_TYPE), URIRef(RML_IRI)))

    # branch 2: constant is a blank node, no termtype -> gets BlankNode
    tm2 = URIRef(EX + "tm2")
    g.add((tm2, URIRef(RML_CONSTANT), BNode("c2")))

    # branch 3: constant is a literal, no termtype -> gets Literal
    tm3 = URIRef(EX + "tm3")
    g.add((tm3, URIRef(RML_CONSTANT), Literal("hello")))

    # branch 4: object map with a reference, no termtype -> gets Literal
    om4 = URIRef(EX + "om4")
    pom4 = URIRef(EX + "pom4")
    g.add((pom4, URIRef(RML_OBJECT_MAP), om4))
    g.add((om4, URIRef(RML_REFERENCE), Literal("col")))

    # branch 5: referencing object map inherits termtype from parent subject
    parent_tm = URIRef(EX + "parent_tm")
    parent_subject_map = URIRef(EX + "parent_subject_map")
    g.add((parent_tm, URIRef(RML_SUBJECT_MAP), parent_subject_map))
    g.add((parent_subject_map, URIRef(RML_TERM_TYPE), URIRef(RML_IRI)))
    tm5 = URIRef(EX + "tm5")
    g.add((tm5, URIRef(RML_PARENT_TRIPLES_MAP), parent_tm))

    # branch 6: subject map with no termtype anywhere -> defaults to IRI
    x6 = URIRef(EX + "x6")
    tm6 = URIRef(EX + "tm6")
    g.add((x6, URIRef(RML_SUBJECT_MAP), tm6))

    return g


VERDICT = run_pair(
    __file__,
    entry='_complete_termtypes',
    calls=[lambda: ((_make_graph(),), {})],
)

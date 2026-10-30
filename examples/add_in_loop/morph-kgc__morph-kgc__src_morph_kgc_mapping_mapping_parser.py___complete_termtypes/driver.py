"""Validation driver for morph-kgc__morph-kgc__src_morph_kgc_mapping_mapping_parser.py___complete_termtypes.

Establishes semantic equivalence of original.py and translated.ldpy.

The graph holds, for each of the six completion rules, a map that must be
completed AND a neighbour that already has an rr:termType and must stay
untouched (so that dropping `!bound(?termtype)` from a FILTER is a diff):

  1. quotedTriplesMap: tm1 (completed), tm1b (has a termType);
  2. constant blank node: tm2 / tm2b; 3. constant literal: tm3 / tm3b
     (tm2b/tm3b already have a termType);
  4. object maps: om4 (reference), om4b (reference, has a termType), and
     one object map for each of execution / languageMap / datatypeMap alone
     (om4e, om4l, om4d: none has a reference, so each `bound(...)` term of
     the FILTER is the only reason for the Literal completion);
  5. referencing object map inheriting the parent's subject-map termType;
  6. the default IRI for every term map reached from subjectMap,
     predicateMap, objectMap and graphMap (x6 / x6p / x6g: a missing
     predicateMap or graphMap from the final list is a diff).
"""
from rdflib import Graph, URIRef, Literal, BNode

from rdfeval.harness import run_pair
from rml_constants import (
    RML_QUOTED_TRIPLES_MAP, RML_TERM_TYPE, RML_RDF_STAR_TRIPLE,
    RML_CONSTANT, RML_BLANK_NODE, RML_LITERAL, RML_OBJECT_MAP,
    RML_REFERENCE, RML_EXECUTION, RML_LANGUAGE_MAP, RML_DATATYPE_MAP,
    RML_PARENT_TRIPLES_MAP, RML_SUBJECT_MAP, RML_PREDICATE_MAP,
    RML_GRAPH_MAP, RML_IRI,
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
    # neighbour: blank-node constant that already has a termtype -> untouched
    tm2b = URIRef(EX + "tm2b")
    g.add((tm2b, URIRef(RML_CONSTANT), BNode("c2b")))
    g.add((tm2b, URIRef(RML_TERM_TYPE), URIRef(RML_IRI)))

    # branch 3: constant is a literal, no termtype -> gets Literal
    tm3 = URIRef(EX + "tm3")
    g.add((tm3, URIRef(RML_CONSTANT), Literal("hello")))
    # neighbour: literal constant that already has a termtype -> untouched
    tm3b = URIRef(EX + "tm3b")
    g.add((tm3b, URIRef(RML_CONSTANT), Literal("hello")))
    g.add((tm3b, URIRef(RML_TERM_TYPE), URIRef(RML_IRI)))

    # branch 4: object map with a reference, no termtype -> gets Literal
    om4 = URIRef(EX + "om4")
    pom4 = URIRef(EX + "pom4")
    g.add((pom4, URIRef(RML_OBJECT_MAP), om4))
    g.add((om4, URIRef(RML_REFERENCE), Literal("col")))
    # neighbour: object map with a reference that already has a termtype
    om4b = URIRef(EX + "om4b")
    g.add((URIRef(EX + "pom4b"), URIRef(RML_OBJECT_MAP), om4b))
    g.add((om4b, URIRef(RML_REFERENCE), Literal("col")))
    g.add((om4b, URIRef(RML_TERM_TYPE), URIRef(RML_IRI)))
    # object maps carrying only one of execution / languageMap / datatypeMap
    for i, prop in enumerate((RML_EXECUTION, RML_LANGUAGE_MAP, RML_DATATYPE_MAP)):
        om = URIRef(EX + "om4_" + str(i))
        g.add((URIRef(EX + "pom4_" + str(i)), URIRef(RML_OBJECT_MAP), om))
        g.add((om, URIRef(prop), URIRef(EX + "val" + str(i))))

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
    # same default for a predicate map and a graph map without termtype
    g.add((x6, URIRef(RML_PREDICATE_MAP), URIRef(EX + "tm6p")))
    g.add((x6, URIRef(RML_GRAPH_MAP), URIRef(EX + "tm6g")))

    return g


VERDICT = run_pair(
    __file__,
    entry='_complete_termtypes',
    calls=[lambda: ((_make_graph(),), {})],
)

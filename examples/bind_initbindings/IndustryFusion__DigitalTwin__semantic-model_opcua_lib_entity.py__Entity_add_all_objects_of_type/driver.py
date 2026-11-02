"""Validation driver for IndustryFusion__DigitalTwin__semantic-model_opcua_lib_entity.py__Entity_add_all_objects_of_type.

The method reads `g` (fixture.ttl, parsed fresh per side) and writes into
`self.e`, which is what the harness compares (with the logged messages),
call by call. Ten calls:

  n1       shares ex:T1 with n2 and n3, and ex:Base2 with n5 -- but Base2 is
           a two-step subclass of opcua:BaseNodeClass, so n5 must NOT come
  n3       two classes: n1 and n2 through T1, n4 through T2
  lonely   no neighbour: only its own triples
  untyped  no rdf:type: only its own triples
  n5       only a BaseNodeClass subclass: only its own triples
  absent   not in the graph: nothing
  nil      rdf:nil: the method returns at once
  list     a blank node: the members of the RDF list (n4, lonely)
  list2    a list of two blank nodes of the same class: each finds the other
  not-list a blank node with no rdf:first: nothing

`self.e` already holds a triple that must survive.
"""
import re

from rdflib import Graph, Literal, RDF, URIRef

from rdfeval.harness import fixture_graph, run_pair
from context_shim import Entity

EX = "http://example.org/"
HERE = __file__.rsplit("/", 1)[0]


def _entity():
    ent = Entity()
    ent.e.add((URIRef(EX + "kept"), URIRef(EX + "p"), Literal("kept")))
    return ent


def _call(obj):
    """obj: a term, or a function of the fresh graph (a blank node of it)."""
    def make():
        g = fixture_graph(HERE + "/fixture.ttl")
        return (_entity(), g, obj(g) if callable(obj) else obj), {}
    return make


def _value(subject, predicate):
    return lambda g: g.value(URIRef(EX + subject), URIRef(EX + predicate))


def _mask_bnodes(text):
    """The log line names the blank node it is handed (`... of type n3f2a...`);
    the parser mints a different id on each side. The ids are dropped, nothing
    else."""
    return re.sub(r"\bn[0-9a-f]{28,}\b", "_:b", text)


VERDICT = run_pair(
    __file__,
    entry="add_all_objects_of_type",
    fixture="fixture.ttl",
    stdout_filter=_mask_bnodes,
    calls=[
        _call(URIRef(EX + "n1")),
        _call(URIRef(EX + "n3")),
        _call(URIRef(EX + "lonely")),
        _call(URIRef(EX + "untyped")),
        _call(URIRef(EX + "n5")),
        _call(URIRef(EX + "absent")),
        _call(RDF.nil),
        _call(_value("holder", "items")),
        _call(_value("holder2", "items")),
        _call(_value("holder3", "single")),
    ],
)

"""Validation driver for ArangoDB-Community__ArangoRDF__arango_rdf_main.py__ArangoRDF___add_adb_col_statement.

The region is a method: the graph it writes is `self.__adb_col_statements`,
reached through the receiver.  Each call fixture builds a fresh receiver (the
callable is invoked once per side), so the harness compares the mutated graph
as argument 0 — ArangoRDFStub.__eq__ compares it by RDF isomorphism.

The four calls cover the three branches: add on an empty graph, the early
return when a statement already exists, and the `overwrite=True` wildcard
removal — once over two competing collection statements, once with
neighbouring triples (another subject, another predicate) that must survive.

Repair pass (2026-10-27) adds the cases that tell the existence test and the
wildcard apart from their over-broad neighbours, and the term types the
repository really passes (its callers hand over terms read from the graph
being converted: URIRef, and BNode for reified statements):

* `neighbours_no_overwrite`: S has a triple on ANOTHER predicate and another
  subject has the collection statement, but S has none -> the statement must
  be ADDED.  Kills an existence test widened to any predicate
  (`m{ {subject} ?p ?o }`) or to any subject (`m{ ?s p ?o }`).
* `overwrite_on_empty`, `overwrite_same_value`: the wildcard removal finds
  nothing / finds the very statement it re-adds.
* `bnode_*`: a blank-node subject, with and without overwrite, in a graph
  holding another blank node with a collection statement (a BNode is not a
  variable, and does not match another BNode).
* `empty_collection_name`: `Literal("")` is still written (a falsy name).
* `literal_subject`: a Literal subject (`explicit_type_map` is fed the
  objects of rdf:type, which can be literals) is accepted by Graph.add and
  written by `+{ }` alike.

NOT exercised: `subject=None`.  The repository reaches it (the
`rdf_graph.value(s, RDF.object)` of a reified statement missing its
rdf:object, main.py:3641, :3735, :3820, always with overwrite=True) but the
original then wipes every `adb:collection` statement and raises
AssertionError ("Subject None must be an rdflib term") from `Graph.add`,
where `{subject}` turns None into Literal("None") and writes it silently.
That is the language's known `{expr}`-is-None gap, on an input where the
original aborts; see meta.json `repair.remaining`.
"""
from rdflib import BNode, Literal, URIRef

from context_shim import ADB_COL_URI, ArangoRDFStub
from rdfeval.harness import run_pair

S = URIRef("http://example.com/Person/1")
OTHER = URIRef("http://example.com/Person/2")
OTHER_P = URIRef("http://example.com/label")


def stub(*triples):
    s = ArangoRDFStub()
    for t in triples:
        s.statements().add(t)
    return s


def empty_no_overwrite():
    return ((stub(), S, "Person"), {})


def already_there_no_overwrite():
    return ((stub((S, ADB_COL_URI, Literal("Person"))), S, "Employee"), {})


def two_statements_overwrite():
    return ((stub((S, ADB_COL_URI, Literal("Person")),
                  (S, ADB_COL_URI, Literal("Employee"))),
             S, "Human"), {"overwrite": True})


def neighbours_overwrite():
    return ((stub((S, ADB_COL_URI, Literal("Person")),
                  (S, OTHER_P, Literal("kept: another predicate")),
                  (OTHER, ADB_COL_URI, Literal("kept: another subject"))),
             S, "Human"), {"overwrite": True})


B1, B2 = BNode("b1"), BNode("b2")


def neighbours_no_overwrite():
    return ((stub((S, OTHER_P, Literal("another predicate, no collection")),
                  (OTHER, ADB_COL_URI, Literal("another subject, has one"))),
             S, "Person"), {})


def overwrite_on_empty():
    return ((stub(), S, "Person"), {"overwrite": True})


def overwrite_same_value():
    return ((stub((S, ADB_COL_URI, Literal("Person"))),
             S, "Person"), {"overwrite": True})


def bnode_no_overwrite():
    return ((stub((B2, ADB_COL_URI, Literal("other bnode, has one"))),
             B1, "Class"), {})


def bnode_already_there():
    return ((stub((B1, ADB_COL_URI, Literal("Class"))), B1, "Property"), {})


def bnode_overwrite():
    return ((stub((B1, ADB_COL_URI, Literal("Class")),
                  (B2, ADB_COL_URI, Literal("kept: other bnode"))),
             B1, "Property"), {"overwrite": True})


def empty_collection_name():
    return ((stub(), S, ""), {})


def literal_subject():
    return ((stub((OTHER, ADB_COL_URI, Literal("kept"))),
             Literal("a literal in subject position"), "Class"), {})


VERDICT = run_pair(
    __file__,
    entry='__add_adb_col_statement',
    calls=[empty_no_overwrite, already_there_no_overwrite,
           two_statements_overwrite, neighbours_overwrite,
           neighbours_no_overwrite, overwrite_on_empty, overwrite_same_value,
           bnode_no_overwrite, bnode_already_there, bnode_overwrite,
           empty_collection_name, literal_subject],
)

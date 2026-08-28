"""Validation driver for ArangoDB-Community__ArangoRDF__arango_rdf_main.py__ArangoRDF___add_adb_col_statement.

The region is a method: the graph it writes is `self.__adb_col_statements`,
reached through the receiver.  Each call fixture builds a fresh receiver (the
callable is invoked once per side), so the harness compares the mutated graph
as argument 0 — ArangoRDFStub.__eq__ compares it by RDF isomorphism.

The four calls cover the three branches: add on an empty graph, the early
return when a statement already exists, and the `overwrite=True` wildcard
removal — once over two competing collection statements, once with
neighbouring triples (another subject, another predicate) that must survive.
"""
from rdflib import Literal, URIRef

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


VERDICT = run_pair(
    __file__,
    entry='__add_adb_col_statement',
    calls=[empty_no_overwrite, already_there_no_overwrite,
           two_statements_overwrite, neighbours_overwrite],
)

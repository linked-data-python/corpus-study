"""Validation driver for synaptixs/ontomesh src/cq_tester.py::_run_cq_sparql.

`_run_cq_sparql(graph, cq)` runs the competency question's `sparql_equiv` (a
whole query, received as DATA) after a fixed PREFIX block and returns
(row count, status).  The fixture is a small ontology in the prologue's `:`
namespace.  Calls, all through the same function:

  * graph None; no `sparql_equiv`; a blank one: (0, "N/A");
  * a query that has rows, with expected_non_empty True (PASS) and False
    (FAIL), through each prefix of the prologue (`:`, owl:, rdfs:, skos:,
    prov:), so that dropping or changing a line of the prologue shows;
  * a query with no rows, expected_non_empty False (PASS) and True (FAIL);
  * row counts that tell the patterns apart (6 classes, 4 labelled, 2
    subclasses of :Employee, one skos:definition, one prov:wasDerivedFrom);
  * a query that is not SPARQL, and one using a prefix nobody declared:
    ERROR; a query that redeclares `:` to another IRI (no row, FAIL) and one
    that redeclares it to the same IRI (one row, PASS);
  * a cq without `expected_non_empty` (KeyError, compared as a raise);
"""
from pathlib import Path

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"


def call(cq, graph=True):
    def _make():
        return (fixture_graph(FIXTURE) if graph else None, cq), {}
    return _make


def cq(q, expected=True):
    return {"sparql_equiv": q, "expected_non_empty": expected}


VERDICT = run_pair(
    __file__,
    entry='_run_cq_sparql',
    calls=[
        call(cq("SELECT ?c WHERE { ?c a owl:Class }"), graph=False),
        call({"expected_non_empty": True}),
        call(cq("   \n  ")),
        call(cq("SELECT ?c WHERE { ?c a owl:Class }", True)),
        call(cq("SELECT ?c WHERE { ?c a owl:Class }", False)),
        call(cq("SELECT ?c WHERE { ?c rdfs:label ?l }", True)),
        call(cq("SELECT ?c WHERE { ?c rdfs:subClassOf :Employee }", True)),
        call(cq("SELECT ?c WHERE { ?c skos:definition ?d }", True)),
        call(cq("SELECT ?c WHERE { ?c prov:wasDerivedFrom ?x }", True)),
        call(cq("SELECT ?l WHERE { :Employee rdfs:label ?l }", True)),
        call(cq("SELECT ?l WHERE { :Employee rdfs:label ?l }", False)),
        call(cq("ASK { :Manager rdfs:subClassOf :Employee }", True)),
        call(cq("SELECT ?c WHERE { ?c rdfs:label \"nothing\" }", False)),
        call(cq("SELECT ?c WHERE { ?c rdfs:label \"nothing\" }", True)),
        call(cq("SELECT ?c WHERE { ?c a :Missing }", True)),
        call(cq("this is not sparql", True)),
        call(cq("SELECT ?c WHERE { ?c a nope:Person }", True)),
        call(cq("PREFIX : <http://other/>\nSELECT ?c WHERE { :Employee a owl:Class }", True)),
        call(cq("PREFIX : <https://ontology.example.com/enterprise/>\nSELECT ?c WHERE { :Employee a ?c }", True)),
        call({"sparql_equiv": "SELECT ?c WHERE { ?c a owl:Class }"}),
    ],
)

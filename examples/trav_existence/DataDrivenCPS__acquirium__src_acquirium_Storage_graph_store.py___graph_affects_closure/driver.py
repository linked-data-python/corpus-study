"""Validation driver for DataDrivenCPS__acquirium__src_acquirium_Storage_graph_store.py___graph_affects_closure.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).

`_graph_affects_closure(graph)` reads the WHOLE graph -- there is no subject
or predicate argument to vary within one fixture -- so exercising both
`bool(m{ }) or bool(m{ })` disjuncts needs three distinct graphs, not three
calls against one fixture.ttl:

  * fixture.ttl itself: neither disjunct matches -> False;
  * an inline graph with only owl:imports -> True through the first m{ };
  * an inline graph with only rdf:type owl:Ontology -> True through the
    second m{ }, proving the `or` does not depend on the first disjunct.
"""
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import run_pair, fixture_graph

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"

_IMPORTS_ONLY = """
@prefix ex: <http://example.org/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

ex:a owl:imports <http://example.org/other> .
"""

_ONTOLOGY_TYPE_ONLY = """
@prefix ex: <http://example.org/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

ex:onto rdf:type owl:Ontology .
"""


def _parsed(data):
    return lambda: ((Graph().parse(data=data, format="turtle"),), {})


VERDICT = run_pair(
    __file__,
    entry='_graph_affects_closure',
    fixture="fixture.ttl",
    calls=[
        lambda: ((fixture_graph(FIXTURE),), {}),  # neither pattern -> False
        _parsed(_IMPORTS_ONLY),                    # owl:imports only -> True
        _parsed(_ONTOLOGY_TYPE_ONLY),               # rdf:type owl:Ontology only -> True
    ],
)

"""Validation driver for RDFLib__prez__tests_test_endpoints_spaceprez.py__test_feature.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  Each call parses a fresh graph for each side.

The region is a pytest test whose whole body is
``assert next(response_graph.triples((Feature1, RDF.type, GEO.Feature)))``:
a fully bound triple, so what it decides is "present -> returns None" or
"absent -> raises".  The harness compares raises (type and message), so the
absent calls check the exception the translation raises against the
original's ``StopIteration('')``.  The real repository parses the HTTP
response into a plain ``Graph`` (tests/test_endpoints_spaceprez.py,
``Graph().parse(data=g_text)``): a set of triples, so the fully bound
pattern matches at most once and there is no "two solutions" case.

Calls, and what each one exercises:

0. ``fixture.ttl``: the triple is present, next to neighbours that share
   two of its three terms. The region returns None.
1. an empty graph: zero solutions, nothing else. The region raises.
2. absent; only ``Feature2 a geo:Feature`` (same predicate and object, other
   subject): a pattern widened to ``?s rdf:type geo:Feature`` would pass.
3. absent; only ``Feature1 a dcat:Dataset`` (same subject and predicate,
   other object): a pattern widened to ``Feature1 rdf:type ?t`` would pass.
4. absent; only ``Feature1 rdfs:seeAlso geo:Feature`` (same subject and
   object, other predicate): a pattern widened to ``Feature1 ?p geo:Feature``
   would pass.

Each absent call holds a single neighbour, so a widened term is the only
thing that could make that call succeed.
"""
from rdflib import Graph

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = "fixture.ttl"

PREFIXES = """\
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix geo: <http://www.opengis.net/ont/geosparql#> .
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix sp: <https://example.com/spaceprez/> .
"""

ABSENT_CASES = [
    "",                                         # 1. empty graph
    "sp:Feature2 a geo:Feature .",              # 2. other subject
    "sp:Feature1 a dcat:Dataset .",             # 3. other object
    "sp:Feature1 rdfs:seeAlso geo:Feature .",   # 4. other predicate
]


def from_fixture():
    return ((fixture_graph(FIXTURE),), {})


def from_turtle(body):
    def case():
        return ((Graph().parse(data=PREFIXES + body, format="turtle"),), {})
    return case


VERDICT = run_pair(
    __file__,
    entry='test_feature',
    fixture=FIXTURE,
    calls=[from_fixture] + [from_turtle(body) for body in ABSENT_CASES],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)

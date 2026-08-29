"""Validation driver for NextCenturyCorporation__AIDA-Interchange-Format__python_aida_interchange_aifutils.py__get_type_assertions.

`get_type_assertions` reads a graph -- the reading oracle applies (design
record corpus/405) -- but the function needs both a graph and a URIRef, so
the fixture is built here, in Python, through `calls=`, with the same care a
`fixture.ttl` would need: several solutions, the zero-solution case, and
neighbouring triples that must not match.

No store promises an order over query solutions, and the region does not
sort its own result, so `ordered=False`.
"""
from rdflib import Graph, Namespace, RDF
from rdfeval.harness import run_pair

EX = Namespace("http://example.org/")


def _graph_with_matches():
    g = Graph()
    g.bind("ex", EX)
    # Two type assertions about obj1 -- two solutions.
    g.add((EX.ta1, RDF.type, RDF.Statement))
    g.add((EX.ta1, RDF.predicate, RDF.type))
    g.add((EX.ta1, RDF.subject, EX.obj1))
    g.add((EX.ta2, RDF.type, RDF.Statement))
    g.add((EX.ta2, RDF.predicate, RDF.type))
    g.add((EX.ta2, RDF.subject, EX.obj1))
    # neighbourhood: a Statement about obj1, but asserting a different
    # predicate (not rdf:type) -> must not match.
    g.add((EX.ta3, RDF.type, RDF.Statement))
    g.add((EX.ta3, RDF.predicate, EX.otherProp))
    g.add((EX.ta3, RDF.subject, EX.obj1))
    # neighbourhood: a type assertion, but about a DIFFERENT subject -> must
    # not match a call for obj1.
    g.add((EX.ta4, RDF.type, RDF.Statement))
    g.add((EX.ta4, RDF.predicate, RDF.type))
    g.add((EX.ta4, RDF.subject, EX.obj2))
    return g


def _call_with_matches():
    return (_graph_with_matches(), EX.obj1), {}


def _call_zero_solutions():
    # ex:obj3 has no type assertions at all in this graph: the
    # zero-solution case.
    return (_graph_with_matches(), EX.obj3), {}


VERDICT = run_pair(
    __file__,
    entry='get_type_assertions',
    calls=[_call_with_matches, _call_zero_solutions],
    ordered=False,
)

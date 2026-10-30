"""Validation driver for NextCenturyCorporation__AIDA-Interchange-Format__python_aida_interchange_aifutils.py__get_type_assertions.

`get_type_assertions` reads a graph -- the reading oracle applies (design
record corpus/405) -- but the function needs both a graph and a URIRef, so
the fixture is built here, in Python, through `calls=`, with the same care a
`fixture.ttl` would need: several solutions, the zero-solution case, and
neighbouring triples that must not match.

No store promises an order over query solutions, and the region does not
sort its own result, so `ordered=False`.

Neighbours, each excluded by exactly one line of the pattern: ta3 (rdf:type
Statement about obj1 but another predicate: excluded by the rdf:predicate
line), ta4 (a type assertion about obj2: excluded by the bound subject),
ta5 and ta6 (predicate rdf:type and subject obj1 but not typed
rdf:Statement -- ta5 untyped, ta6 typed ex:NotAStatement: excluded only by
the `?typeAssertion a rdf:Statement` line).
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
    # neighbourhood: a node with predicate rdf:type and subject obj1 that is
    # NOT typed rdf:Statement (a bare reification-looking resource) -> must
    # not match; only the `?typeAssertion a rdf:Statement` line excludes it.
    g.add((EX.ta5, RDF.predicate, RDF.type))
    g.add((EX.ta5, RDF.subject, EX.obj1))
    # same, typed as something else than rdf:Statement.
    g.add((EX.ta6, RDF.type, EX.NotAStatement))
    g.add((EX.ta6, RDF.predicate, RDF.type))
    g.add((EX.ta6, RDF.subject, EX.obj1))
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

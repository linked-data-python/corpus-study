"""Validation driver for calipho-sib__nextprot-scripts__src_polish-rdf_pylode_pyLODE-2.13.2_pylode_profiles_prof.py__Prof__expand_graph.

The region READS a graph and rewrites it in place: the sources of
rdfs:label, rdfs:comment, dcterms:creator/contributor/publisher are removed
(`remove((s, P, o))`, fully bound, in sets of three or four per value) and
replaced by the one expanded triple, and the objects of prof:hasResource are
typed.  `_expand_graph` returns nothing, so the oracle is the state of the
graph the method leaves behind from the same input on both sides: the harness
compares the argument `self` after the call, graph by isomorphism and prefix
bindings by name.

The only context is the object the method hangs on, `Prof`, reduced to its `G`
attribute (pylode_context.py).  The fixture has, for each loop, several
sources, one subject carrying the same value through all the sources (the
loop removes a triple a later generator would have yielded), and neighbours
that share two of three terms with a removed triple (same subject and value
under another predicate, same value on another subject) and must stay.

Calls: the whole fixture, a graph with nothing to expand (zero solutions:
nothing may change) and the fixture with its dc:title triples already turned
into rdfs:label.
"""
from pathlib import Path

from rdflib import Graph

from pylode_context import Prof
from rdfeval.harness import fixture_graph, run_pair

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"


def whole_fixture():
    return ((Prof(fixture_graph(FIXTURE)),), {})


def nothing_to_expand():
    g = Graph()
    g.parse(data="""
        @prefix ex: <http://example.org/> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        ex:a ex:p ex:b ; rdfs:label "kept" ; rdfs:comment "kept too" .
    """, format="turtle")
    return ((Prof(g),), {})


def titles_already_moved():
    from rdflib.namespace import DC, RDFS
    g = fixture_graph(FIXTURE)
    doc = Prof(g)
    for s, o in list(g.subject_objects(DC.title)):
        g.remove((s, DC.title, o))
        g.add((s, RDFS.label, o))
    return ((doc,), {})


VERDICT = run_pair(
    __file__,
    entry="_expand_graph",
    fixture="fixture.ttl",
    calls=[whole_fixture, nothing_to_expand, titles_already_moved],
)

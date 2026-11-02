"""Validation driver for calipho-sib__nextprot-scripts__src_polish-rdf_pylode_pyLODE-2.13.2_pylode_profiles_ontdoc.py__OntDoc__expand_graph.

The region READS a graph and rewrites it in place (it copies the source
properties of dcterms:title/description/creator/contributor/publisher, types
the properties, classes and restrictions, and removes the agents' source
triples), so the oracle is the state of the graph the method leaves behind,
from the same input graph on both sides.  `_expand_graph` returns nothing: the
harness compares the argument `self` after the call, graph by isomorphism and
prefix bindings by name.

The only context is the object the method hangs on, `OntDoc`, reduced to its
`G` attribute (pylode_context.py).  The fixture is one graph with, for each
loop of the region, subjects that must be picked up, several sources on one
subject, a subject with no source, and -- for the removals -- triples sharing
two of their three terms with a triple that goes (same subject and agent under
another predicate, same agent under another subject) which must stay.  The
three `dc:`/`sdo:` removals of the creator loop are fully bound, so a removal
widened to a wildcard is caught only by those neighbours.

Calls: the fixture graph (everything), a graph with no source triple at all
(zero solutions: nothing may change), and the fixture graph with its
dc:creator triples already turned into dcterms:creator (the creator loop then
starts from sdo:creator and sdo:author only).
"""
from pathlib import Path

from rdflib import Graph

from pylode_context import OntDoc
from rdfeval.harness import fixture_graph, run_pair

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"


def whole_fixture():
    return ((OntDoc(fixture_graph(FIXTURE)),), {})


def nothing_to_expand():
    g = Graph()
    g.parse(data="""
        @prefix ex: <http://example.org/> .
        @prefix dcterms: <http://purl.org/dc/terms/> .
        ex:a ex:p ex:b ; dcterms:title "kept" ; dcterms:creator ex:c .
    """, format="turtle")
    return ((OntDoc(g),), {})


def creators_already_moved():
    from rdflib.namespace import DC, DCTERMS
    g = fixture_graph(FIXTURE)
    doc = OntDoc(g)
    for s, o in list(g.subject_objects(DC.creator)):
        g.remove((s, DC.creator, o))
        g.add((s, DCTERMS.creator, o))
    return ((doc,), {})


VERDICT = run_pair(
    __file__,
    entry="_expand_graph",
    fixture="fixture.ttl",
    calls=[whole_fixture, nothing_to_expand, creators_already_moved],
)

"""Validation driver for emmo-repo__domain-electrochemistry__.github_scripts_check_iri_resolution.py__ontology_subject.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

`ontology_subject` takes a second argument (`source`, used only in the
raised message on the zero-solution path) beyond the graph, so `calls=`
supplies both.  In the repository (check_iri_resolution.py:77) the graph is
always one parsed from Turtle, never None.

Each call decides something the region decides:

- call 0, `fixture.ttl`: two solutions (onto1, onto2) -- the region returns
  whichever the store yields first -- plus neighbours sharing two of the
  three terms of `?s rdf:type owl:Ontology` that must NOT match.
- call 1, empty graph: zero solutions, the loop falls through to the raise.
  The harness compares a raise as an outcome (type and message), so this
  kills a translation that returned None instead (`if True:` mutant) or
  changed the message.
- call 2, the neighbours alone (`fixture_neighbours.ttl`): still zero
  solutions -- a pattern widened to `?p` or to `?o` would return a subject.
- call 3, a single blank-node ontology: a BNode subject comes back as is.
- call 4, the IRI `<>` (URIRef(""), a FALSY str) typed owl:Ontology: the
  original returns it; a guard `if subject:` in place of `is not None`
  would raise instead.
"""
import rdflib
from rdfeval.harness import fixture_graph, run_pair


def _call():
    return (fixture_graph("fixture.ttl"), "test-source"), {}


def _empty():
    return (rdflib.Graph(), "empty-source"), {}


def _neighbours():
    return (fixture_graph("fixture_neighbours.ttl"), "nb-source"), {}


def _bnode():
    g = rdflib.Graph()
    g.add((rdflib.BNode(), rdflib.RDF.type, rdflib.OWL.Ontology))
    return (g, "bnode-source"), {}


def _falsy_iri():
    g = rdflib.Graph()
    g.add((rdflib.URIRef(""), rdflib.RDF.type, rdflib.OWL.Ontology))
    return (g, "falsy-source"), {}


VERDICT = run_pair(
    __file__,
    entry='ontology_subject',
    fixture="fixture.ttl",
    calls=[_call, _empty, _neighbours, _bnode, _falsy_iri],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets. Not that
    # it matters here: the entry point returns a single term, not a sequence.
)

"""Validation driver for ArangoDB-Community__ArangoRDF__tests_test_main.py__test_rpt_case_15_4.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405). `fixture.ttl` is parsed fresh for each side.

`get_mary_likes_matt_05(rdf_graph, certainty, certainty_val_05)` takes two
extra arguments the enclosing test builds locally (see original.py), so a
bare `fixture=` (which calls entry with only the parsed graph) is not
enough here -- each call below parses its own fixture graph and supplies
its own `certainty` / `certainty_val_05` term pair.

Three calls exercise the (predicate, object) -> subject lookup the stratum
(trav_single_value) is about, all against the SAME fixture.ttl:
  * val_05  -- ex:certainty "0.5"^^xsd:decimal matches ex:mary_likes_matt_05,
               the ONE among three certainty-carrying statements.
  * val_075 -- ex:certainty "0.75"^^xsd:decimal matches the second one:
               proves the lookup is keyed on the exact object, not just
               "some certainty value".
  * val_missing -- ex:certainty "0.42"^^xsd:decimal matches nothing: the
               ZERO-solution case, where g.value() and m{ }.first() must
               both answer None.
Neither call ever matches ex:weight "0.5"^^xsd:decimal (same value, wrong
predicate) or ex:certainty 0.9 (right predicate, wrong object) --
fixture.ttl's neighbourhood.

Two more inputs (added at repair, 2026-10-30):
  * fixture_15_4.trig, the graph the real test reads, parsed into a
    ConjunctiveGraph as conftest.py's get_rdf_graph does: the four lookups
    of test_main.py:1670-1673 -- (foo, "bar") and (certainty, 0.75 / 1)
    find BLANK-NODE subjects in named graphs, (certainty, 0.5) an IRI in
    ex:Graph1; `Literal(1)` is the Python int the test passes.
    The harness compares any two blank nodes as equal, so these calls prove
    the lookup reaches a blank-node subject across named graphs, not which
    one; fixture_dup.ttl proves the choice, on IRIs.
  * fixture_dup.ttl, several subjects for one (predicate, object):
      dup     -- (certainty, 0.6): ex:dupA and ex:dupB both match, the first
                 the store yields comes back on both sides (a last-solution or
                 `.one()` lookup would differ); ex:w, first in the file, has
                 the same object under ex:weight (a lookup ignoring the
                 predicate would return it);
      lexical -- (certainty, "0.5"^^xsd:decimal) where only "0.50" is
                 present: g.value matches terms, not values -> None.
"""
from rdflib import Literal, Namespace, URIRef

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = "fixture.ttl"
EX = Namespace("http://example.org/")
XSD_DECIMAL = URIRef("http://www.w3.org/2001/XMLSchema#decimal")


def _call(value: str):
    def make():
        g = fixture_graph(FIXTURE)
        certainty = EX.certainty
        certainty_val = Literal(value, datatype=XSD_DECIMAL)
        return ((g, certainty, certainty_val), {})
    return make


val_05 = _call("0.5")
val_075 = _call("0.75")
val_missing = _call("0.42")


def _trig(predicate: str, value):
    def make():
        from rdflib import ConjunctiveGraph
        g = ConjunctiveGraph()
        g.parse("fixture_15_4.trig", format="trig")
        return ((g, URIRef("http://example.com/" + predicate), value), {})
    return make


def _dup(value: str):
    def make():
        g = fixture_graph("fixture_dup.ttl")
        return ((g, EX.certainty, Literal(value, datatype=XSD_DECIMAL)), {})
    return make


VERDICT = run_pair(
    __file__,
    entry='get_mary_likes_matt_05',
    fixture=FIXTURE,
    calls=[val_05, val_075, val_missing,
           _trig("foo", Literal("bar")),
           _trig("certainty", Literal("0.5", datatype=XSD_DECIMAL)),
           _trig("certainty", Literal("0.75", datatype=XSD_DECIMAL)),
           _trig("certainty", Literal(1)),
           _dup("0.6"), _dup("0.5")],
)

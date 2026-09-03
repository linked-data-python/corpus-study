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


VERDICT = run_pair(
    __file__,
    entry='get_mary_likes_matt_05',
    fixture=FIXTURE,
    calls=[val_05, val_075, val_missing],
)

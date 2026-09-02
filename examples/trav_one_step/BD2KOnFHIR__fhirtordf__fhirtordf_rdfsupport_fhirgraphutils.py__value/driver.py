"""Validation driver for BD2KOnFHIR__fhirtordf__fhirtordf_rdfsupport_fhirgraphutils.py__value.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

value(g, subject, predicate, asLiteral=False) needs more than the graph, so
`calls=` supplies (subject, predicate[, asLiteral]) explicitly -- the default
single-graph call (`fixture=` alone) does not apply here.

Four calls: (1) plain-literal object, the non-BNode branch; (2) BNode object
carrying a single fhir:value, the BNode branch; (3) asLiteral=True on the
plain-literal case, to exercise the toPython()-vs-Literal choice; (4) a
subject/predicate pair with no matching triple at all -- the zero-solution
case, both sides must return None.
"""
from pathlib import Path

from rdflib import URIRef

from rdfeval.harness import fixture_graph, run_pair

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"

EX = "http://example.org/"
PATIENT1 = URIRef(EX + "patient1")
PATIENT3 = URIRef(EX + "patient3")
PATIENT5 = URIRef(EX + "patient5")
NAME = URIRef(EX + "name")
CODE = URIRef(EX + "code")


def call_plain_literal():
    return ((fixture_graph(FIXTURE), PATIENT1, NAME), {})


def call_plain_literal_as_literal():
    return ((fixture_graph(FIXTURE), PATIENT1, NAME, True), {})


def call_bnode_with_fhir_value():
    return ((fixture_graph(FIXTURE), PATIENT3, CODE), {})


def call_zero_solutions():
    return ((fixture_graph(FIXTURE), PATIENT5, NAME), {})


VERDICT = run_pair(
    __file__,
    entry='value',
    fixture="fixture.ttl",
    calls=[call_plain_literal, call_plain_literal_as_literal,
           call_bnode_with_fhir_value, call_zero_solutions],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)

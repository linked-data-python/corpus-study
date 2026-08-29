"""Validation driver for BD2KOnFHIR__fhirtordf__fhirtordf_rdfsupport_fhirgraphutils.py__codeable_concept_code.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

codeable_concept_code(g, subject, predicate, system=None) needs more than the
graph, so `calls=` supplies (subject, predicate[, system]) explicitly — the
default single-graph call (`fixture=` alone) does not apply here.

Three calls: (1) subject/predicate with two coding solutions and system=None
— both must come back; (2) the same subject/predicate with system pinned to
one of the two codings' system — exactly one must come back; (3) a subject
with no matching predicate at all — the zero-solution case, both sides must
return [].
"""
from pathlib import Path

from rdflib import URIRef

from rdfeval.harness import fixture_graph, run_pair

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"

PATIENT1 = URIRef("http://example.org/patient1")
PATIENT_X = URIRef("http://example.org/patientX")
MARITAL_STATUS = URIRef("http://example.org/maritalStatus")


def call_no_system():
    return ((fixture_graph(FIXTURE), PATIENT1, MARITAL_STATUS), {})


def call_with_system():
    return ((fixture_graph(FIXTURE), PATIENT1, MARITAL_STATUS,
              "http://snomed.info/sct"), {})


def call_zero_solutions():
    return ((fixture_graph(FIXTURE), PATIENT_X, MARITAL_STATUS), {})


VERDICT = run_pair(
    __file__,
    entry='codeable_concept_code',
    fixture="fixture.ttl",
    calls=[call_no_system, call_with_system, call_zero_solutions],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)

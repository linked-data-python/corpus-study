"""Validation driver for BD2KOnFHIR__fhirtordf__fhirtordf_rdfsupport_fhirgraphutils.py__codeable_concept_code.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

codeable_concept_code(g, subject, predicate, system=None) needs more than the
graph, so `calls=` supplies (subject, predicate[, system]) explicitly — the
default single-graph call (`fixture=` alone) does not apply here.

Eight calls (the last five were added because the original, run on its
repository's own `DottedURIRef` equality, now returns data: they make its
result non-empty and discriminating):
(4) a coding system that matches the second, untyped coding (uri None);
(5) a system that matches no coding ([]); (6) the neighbouring subject
patient2, same predicate; (7) the same subject with another predicate;
(8) patient3, whose incomplete codings (no code, no system, neither) are
skipped.  The first three: (1) subject/predicate with two coding solutions and system=None
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


def call_other_system():
    return ((fixture_graph(FIXTURE), PATIENT1, MARITAL_STATUS,
             "http://hl7.org/fhir/v3/MaritalStatus"), {})


def call_unmatched_system():
    return ((fixture_graph(FIXTURE), PATIENT1, MARITAL_STATUS,
             "http://example.org/no-system"), {})


def call_neighbour_subject():
    return ((fixture_graph(FIXTURE), URIRef("http://example.org/patient2"),
             MARITAL_STATUS), {})


def call_other_predicate():
    return ((fixture_graph(FIXTURE), PATIENT1,
             URIRef("http://example.org/otherStatus")), {})


def call_incomplete_codings():
    return ((fixture_graph(FIXTURE), URIRef("http://example.org/patient3"),
             MARITAL_STATUS), {})


def call_zero_solutions():
    return ((fixture_graph(FIXTURE), PATIENT_X, MARITAL_STATUS), {})


VERDICT = run_pair(
    __file__,
    entry='codeable_concept_code',
    fixture="fixture.ttl",
    calls=[call_no_system, call_with_system, call_zero_solutions,
           call_other_system, call_unmatched_system, call_neighbour_subject,
           call_other_predicate, call_incomplete_codings],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)

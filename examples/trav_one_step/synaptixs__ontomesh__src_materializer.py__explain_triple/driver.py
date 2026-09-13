"""Validation driver for synaptixs__ontomesh__src_materializer.py__explain_triple.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

`explain_triple`'s first argument is a *file path*, not a graph, so the
generic `fixture=` wiring (which passes a parsed Graph as the sole argument)
does not apply here: we build the calls by hand, all pointing at the same
`fixture.ttl` on disk.
"""
from pathlib import Path

from rdfeval.harness import run_pair

FIXTURE = str(Path(__file__).resolve().parent / "fixture.ttl")

EX = "http://example.org/"


def _case_two_derivations():
    # ex:s1 ex:p1 ex:o1 is explained by two derivations (ex:deriv1 with
    # one full premise and one incomplete premise, ex:deriv2 with none).
    return ((FIXTURE, EX + "s1", EX + "p1", EX + "o1"), {})


def _case_zero_derivations():
    # ex:s3 ex:p3 ex:o3 is a reified statement with no prov:wasDerivedFrom
    # at all: the pattern matches, the inner loop yields nothing.
    return ((FIXTURE, EX + "s3", EX + "p3", EX + "o3"), {})


def _case_no_matching_statement():
    # Neighbouring data exists (ex:stmt1, ex:stmt2, ex:stmt3) but none of
    # it reifies this triple: zero solutions overall.
    return ((FIXTURE, EX + "s9", EX + "p9", EX + "o9"), {})


VERDICT = run_pair(
    __file__,
    entry='explain_triple',
    calls=[_case_two_derivations, _case_zero_derivations,
           _case_no_matching_statement],
)

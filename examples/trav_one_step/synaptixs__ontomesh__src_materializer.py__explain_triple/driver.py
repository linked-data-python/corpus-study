"""Validation driver for synaptixs__ontomesh__src_materializer.py__explain_triple.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  The lineage file is parsed fresh by each side.

`explain_triple`'s first argument is a *file path*, not a graph, so the
generic `fixture=` wiring (which passes a parsed Graph as the sole argument)
does not apply here: we build the calls by hand.  The arguments are strings,
as the repository passes them (wizard/app.py:1214, tests/test_phase_d_explain.py):
full IRIs, or a quoted literal '"value"' for the object.

The result is a list in store order (no sort in the region), compared in
order: both sides walk graph.triples() of the same parsed file.

fixture.ttl (hand-written, IRIs):

* call 0 -- (s1, p1, o1): two derivations of stmt1; deriv1 carries TWO
  rules, engines and bindings (next(..., None) and .first() must keep the
  same one), one complete and one incomplete premise.  Neighbours that must
  NOT surface, each with its own derivation: stmtA / stmtB / stmtC differ
  from (s1, p1, o1) in exactly one term and hold the missing term under
  rdfs:seeAlso (kills a dropped guard, a guard whose object or predicate is
  widened to a variable, and `?w rdf:subject {s}`); stmtUntyped reifies the
  triple without rdf:type rdf:Statement; derivI hangs off stmt1 through
  prov:wasInfluencedBy.
* call 1 -- (s3, p3, o3): a statement with no derivation (inner zero case).
* call 2 -- (s9, p9, o9): no statement at all (outer zero case).
* call 3 -- (s1, p1, oX): only the near-miss stmtA matches.
* call 4 -- the object given as '<IRI>' (the other spelling _parse_term
  accepts): same derivations as call 0.
* call 5 -- a lineage path that does not exist: [] before any parsing.

lineage_real.ttl (the shape materializer._write_lineage writes: blank
nodes everywhere, typed literals):

* call 6 -- (A, reaches, C): four derivations of a blank-node statement:
  premises reached through toolkit:premise but not prov:used; a rule "",
  a missing engine, bindings "0"^^xsd:integer, invalid JSON, a JSON list;
  premises with falsy literal objects (0, false, "") dropped by
  `ps and pp and po`, one with "x" kept.
* call 7 -- (t1, flag, '"true"'): the object is "true"^^xsd:boolean in the
  file, the query a plain literal: no match (the repository's
  test_shacl_rule_attribution relies on this miss).
* call 8 -- (t2, flag, '"true"'): plain literal object, matches.
* call 9 -- (t3, label, '""'): the empty literal, matches.
"""
from pathlib import Path

from rdfeval.harness import run_pair

HERE = Path(__file__).resolve().parent
FIXTURE = str(HERE / "fixture.ttl")
REAL = str(HERE / "lineage_real.ttl")
MISSING = str(HERE / "no-such-lineage.ttl")

EX = "http://example.org/"
NS = "http://example.org/ns#"


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


def _case_near_miss_object():
    # only ex:stmtA reifies (s1, p1, oX)
    return ((FIXTURE, EX + "s1", EX + "p1", EX + "oX"), {})


def _case_angle_bracket_object():
    # the '<IRI>' spelling of the object
    return ((FIXTURE, EX + "s1", EX + "p1", "<" + EX + "o1>"), {})


def _case_missing_file():
    return ((MISSING, EX + "s1", EX + "p1", EX + "o1"), {})


def _case_real_shape():
    return ((REAL, NS + "A", NS + "reaches", NS + "C"), {})


def _case_typed_literal_miss():
    return ((REAL, NS + "t1", NS + "flag", '"true"'), {})


def _case_plain_literal_hit():
    return ((REAL, NS + "t2", NS + "flag", '"true"'), {})


def _case_empty_literal():
    return ((REAL, NS + "t3", NS + "label", '""'), {})


VERDICT = run_pair(
    __file__,
    entry='explain_triple',
    calls=[_case_two_derivations, _case_zero_derivations,
           _case_no_matching_statement, _case_near_miss_object,
           _case_angle_bracket_object, _case_missing_file,
           _case_real_shape, _case_typed_literal_miss,
           _case_plain_literal_hit, _case_empty_literal],
)

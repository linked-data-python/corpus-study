"""Validation driver for OntoUML__ontouml-json2graph__json2graph_tests_test_main.py__get_recorded_configuration.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  Each fixture is parsed fresh for each side.

The fixture is part of the translation: it must hold several solutions of the
pattern the region reads, the zero-solution case, and neighbouring triples
that must NOT match.

Three calls (the last two added by the mutation audit of 2026-10-31):
  * fixture.ttl -- the nominal case: three used entities, one with a
    prov:value; a second activity using an entity WITH a prov:value, which a
    widened `prov:used` or last `prov:value` read would pick up.
  * fixture_two_values.ttl -- two wasGeneratedBy objects and two prov:value
    literals per entity: value() takes the first and never raises, so
    `.one()` in place of `.first()` dies.
  * fixture_empty_value.ttl -- a used entity whose prov:value is "": the
    existence filter keeps it (the region's assert then fails, on both
    sides), a truthiness filter would not.

Equivalent mutants, not counted: `next(iter(...))` and a widened subject on
the first read -- get_output_artifact asserts that exactly one subject
carries prov:wasGeneratedBy, so that read has at least one solution and no
other subject to widen to.  The prefix binding `@graph metadata_graph` adds
is `prov:`, which json2graph already binds under that name
(transformation_metadata.py:122) and rdflib binds by default: a no-op.
"""
from pathlib import Path

from rdfeval.harness import fixture_graph, run_pair

HERE = Path(__file__).resolve().parent


def _case(name):
    return lambda: ((fixture_graph(HERE / name),), {})


VERDICT = run_pair(
    __file__,
    entry='get_recorded_configuration',
    fixture="fixture.ttl",
    calls=[_case("fixture.ttl"), _case("fixture_two_values.ttl"),
           _case("fixture_empty_value.ttl")],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)

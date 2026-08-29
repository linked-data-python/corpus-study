"""Validation driver for CatholicOS__ontokit-api__ontokit_services_embedding_text_builder.py__build_embedding_text.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

build_embedding_text(graph, entity_uri, entity_type) needs more than the
graph, so `calls=` supplies (entity_uri, entity_type) explicitly -- the
default single-graph call (`fixture=` alone) does not apply here.

Three calls: (1) ex:Animal/"class" -- two labels (primary + extra), a
comment that must win over a definition, one parent filtered out
(owl:Thing) and one kept with its own label, one alt label, and a
non-literal rdfs:label object that must be dropped by the isinstance
filter; (2) ex:WorksAt/"property" -- the subPropertyOf branch and the
"no comment, fall back to definition" branch; (3) ex:Empty/"class" -- the
zero-solution case across every field in the region (falls back to
_local_name, no description, no parents, no alt labels).
"""
from pathlib import Path

from rdflib import Namespace

from rdfeval.harness import fixture_graph, run_pair

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"

EX = Namespace("http://example.org/")


def call_class_with_parents_and_alt():
    return ((fixture_graph(FIXTURE), EX.Animal, "class"), {})


def call_property_definition_fallback():
    return ((fixture_graph(FIXTURE), EX.WorksAt, "property"), {})


def call_zero_solutions():
    return ((fixture_graph(FIXTURE), EX.Empty, "class"), {})


VERDICT = run_pair(
    __file__,
    entry='build_embedding_text',
    fixture="fixture.ttl",
    calls=[call_class_with_parents_and_alt, call_property_definition_fallback,
           call_zero_solutions],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)

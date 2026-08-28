"""Validation driver for laBioSynCare__laBioSynCare.github.io__scripts_sstim-ecosystem-contract.py__check_real_public_artifact.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

The fixture is part of the translation: it must hold several solutions of the
pattern the region reads, the zero-solution case, and neighbouring triples
that must NOT match.

check_real_public_artifact(artifact, label) needs a label string too, so
`calls=` supplies it explicitly — the default single-graph call (`fixture=`
alone) does not apply here. Two calls, same fixture graph, different labels:
the label is plain Python (f-string interpolation, no island), so varying it
also checks that the untranslated half of the function still agrees.
"""
from pathlib import Path

from rdfeval.harness import fixture_graph, run_pair

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"


def call_label_a():
    return ((fixture_graph(FIXTURE), "aggregate-A"), {})


def call_label_b():
    return ((fixture_graph(FIXTURE), "aggregate-B"), {})


VERDICT = run_pair(
    __file__,
    entry='check_real_public_artifact',
    fixture="fixture.ttl",
    calls=[call_label_a, call_label_b],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)

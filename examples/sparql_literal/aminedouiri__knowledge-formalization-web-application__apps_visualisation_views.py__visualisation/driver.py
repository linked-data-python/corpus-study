"""Validation driver for aminedouiri__knowledge-formalization-web-application__apps_visualisation_views.py__visualisation.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

The fixture is part of the translation: it must hold several solutions of the
pattern the region reads, the zero-solution case, and neighbouring triples
that must NOT match.
"""
from rdfeval.harness import run_pair

# `visualisation` reads six ontology files, one per query (see the six
# `*_path` parameters added to restore that binding — meta.json). All six
# are pointed at the single fixture.ttl below, which carries instances of
# every class each query selects, so `calls` is custom rather than the
# default single-graph-argument convention `fixture=` builds.
VERDICT = run_pair(
    __file__,
    entry='visualisation',
    calls=[lambda: ((None,), {
        "tache_path": "fixture.ttl",
        "activite_path": "fixture.ttl",
        "historique_path": "fixture.ttl",
        "phenomene_path": "fixture.ttl",
        "domaine_path": "fixture.ttl",
        "strategie_path": "fixture.ttl",
    })],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
    ordered=False,
)

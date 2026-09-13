"""Validation driver for pangenome__spodgi__test_test_select.py__test_count_distinct_steps.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

The fixture is part of the translation: it must hold several solutions of the
pattern the region reads, the zero-solution case, and neighbouring triples
that must NOT match.
"""
from rdfeval.harness import run_pair

# The region opens a real pangenome graph through the native `spodgi.OdgiStore`
# rdflib store plugin (a C++ extension backed by a binary `.odgi` file). That
# plugin is not installed and its binary fixture cannot be reproduced here —
# see translation_notes in meta.json (classification: excluded). `calls`
# below is only what the entry point's signature needs to be invoked at all;
# it never gets far enough to matter.
VERDICT = run_pair(
    __file__,
    entry='test_count_distinct_steps',
    calls=[lambda: ((), {})],
)

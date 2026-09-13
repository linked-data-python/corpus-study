"""Validation driver for
eliozo__worksheet-generation-with-llms__scripts_weaviate_utils.py__WeaviateUtils_ingest_to_weaviate.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405). `ingest_to_weaviate(self, filename)` reads a `self` for its
Weaviate client and its namespace, and re-parses `filename` itself, so
`calls=` builds that `self` (see context_shim.py) and passes the path to
`fixture.ttl` rather than using the `fixture=` shortcut.

The function's own return value is a fixed status tuple -- what it actually
computed (`data_object`) only shows up as an insert call on the (fake)
Weaviate client, so the oracle is `self.inserted`, compared through
`_Self.__eq__`, not the return value.
"""
from pathlib import Path

from rdfeval.harness import run_pair
from context_shim import make_self

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"


def _case():
    return ((make_self(), str(FIXTURE)), {})


VERDICT = run_pair(
    __file__,
    entry='ingest_to_weaviate',
    calls=[_case],
)

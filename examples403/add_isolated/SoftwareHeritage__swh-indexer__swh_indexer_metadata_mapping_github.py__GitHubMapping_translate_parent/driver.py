"""Validation driver for SoftwareHeritage__swh-indexer__swh_indexer_metadata_mapping_github.py__GitHubMapping_translate_parent.

Establishes semantic equivalence of original.py and translated.ldpy.
translate_parent(self, graph, root, v) mutates `graph` in place and returns
None; `self` is unused by the region's own body (no method on it is called),
so a bare None stands in for it. Each case is a callable so a fresh Graph()
and BNode() are built per side -- the harness invokes `case()` once per
version, and mutable arguments must not leak across the two runs.
"""
from rdfeval.harness import run_pair
from rdflib import BNode, Graph

VERDICT = run_pair(
    __file__,
    entry='translate_parent',
    calls=[
        # html_url present: the guarded triple is added.
        lambda: ((None, Graph(), BNode(),
                  {"html_url": "http://example.org/test-software"}), {}),
        # html_url absent: isinstance(v.get("html_url"), str) is False, no
        # triple is added -- exercises the guard, not just the add.
        lambda: ((None, Graph(), BNode(), {"other_field": "x"}), {}),
        # v is not a dict at all: the isinstance(v, dict) guard short-circuits.
        lambda: ((None, Graph(), BNode(), "not-a-dict"), {}),
    ],
)

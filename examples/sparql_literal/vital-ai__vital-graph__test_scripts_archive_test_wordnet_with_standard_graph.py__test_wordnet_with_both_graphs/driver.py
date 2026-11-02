"""Driver for vital-ai__vital-graph__test_scripts_archive_test_wordnet_with_standard_graph.py__test_wordnet_with_both_graphs.

EXCLUDED (see meta.json): the region cannot run, for two independent reasons.

* `vitalgraph.store.store` and `vitalgraph.optimized_graph` do not exist at the
  pinned commit (7fb3616c2d): they live under archive/archive_vitalgraph_old/,
  so even with the repository's
  `vitalgraph` package on the path the imports of the region fail with
  `ModuleNotFoundError: No module named 'vitalgraph.store'`; in the study venv
  (nothing installed under that name) the error is
  `ModuleNotFoundError: No module named 'vitalgraph'`.
* even with them, `store.open("postgresql+psycopg://postgres@127.0.0.1:5432/
  vitalgraphdb", create=False)` needs a live PostgreSQL holding the WordNet
  graph, and `OptimizedVitalGraph.query` answers text-search queries with
  direct SQL.

This driver is what would prove the pair if a database were there: the entry
point takes nothing and returns nothing, so what is compared is the stdout
(the four result counts and the results of each query), with the wall-clock
durations the region prints blanked on both sides.  The translation itself
was run once, outside the study tree, against a stand-in (an in-memory rdflib
store behind both graph classes, five entities named or not "happy", four
edges): stdout identical to the original's, `equivalent: true`.
"""
import re

from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='test_wordnet_with_both_graphs',
    calls=[((), {})],
    stdout_filter=lambda text: re.sub(r"\d+\.\d{3}s", "<duration>s", text),
)

"""Validation driver for Congruentsys__yurtle-rdflib__src_yurtle_rdflib_store.py__YurtleStore__flush_file.

`demo()` (identical on both sides, appended after the extracted region --
see meta.json) builds a minimal fake `self` (file_states, internal_graph,
writer, _compute_file_hash) and calls `_flush_file(self, path)`, then
reads back the file the region actually wrote (its only RDF-observable
effect) plus the two non-wall-clock state fields it updates.
"""
import re

from rdfeval.harness import run_pair

# Each side's demo() works in a temporary directory of its own, and the
# region logs the path it flushes: the directory's name is not the
# program's meaning.
VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[((), {})],
    stdout_filter=lambda text: re.sub(r"/tmp/tmp\w+", "<tmp>", text),
)

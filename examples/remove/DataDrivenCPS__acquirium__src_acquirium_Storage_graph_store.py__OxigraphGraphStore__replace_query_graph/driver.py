"""Validation driver for DataDrivenCPS__acquirium__src_acquirium_Storage_graph_store.py__OxigraphGraphStore__replace_query_graph.

Establishes semantic equivalence of original.py and translated.ldpy.

The region is a method that mutates one named graph of `self.query_dataset`
and returns nothing, so the pair is compared in module-state mode, driven by
the demo harness both files carry: `replaced_graph` (cleared, then reloaded
from the serialised input), `cleared_graph` (the empty-input early return) and
`neighbour_graph` (a second named graph the clear must not touch).

The bindings the region needs -- `self.query_dataset`, pyoxigraph's
`NamedNode` / `RdfFormat`, and `acquirium.internals._log.timed_debug` -- come
from the context shim `context_shim.py`, which both representations import as
their first line.  See meta.json.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)

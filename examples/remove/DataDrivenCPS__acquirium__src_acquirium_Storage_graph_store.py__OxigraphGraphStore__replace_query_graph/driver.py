"""Validation driver for DataDrivenCPS__acquirium__src_acquirium_Storage_graph_store.py__OxigraphGraphStore__replace_query_graph.

Establishes semantic equivalence of original.py and translated.ldpy.

The region is a method that clears one named graph of `self.query_dataset`
(`target.remove((None, None, None))` / `-{ ?s ?p ?o }`), then reloads it
from the N-Triples of `graph`, and returns nothing.  The bindings it needs
-- `self.query_dataset`, pyoxigraph's `NamedNode` / `RdfFormat`, and
`acquirium.internals._log.timed_debug` -- come from the context shim
`context_shim.py`, which both representations import as their first line.

Two oracles, merged into one verdict:

1. MODULE STATE of the demo harness both files carry (unchanged):
   `replaced_graph`, `neighbour_graph`, `cleared_graph`, compared by
   isomorphism (`_demo_diffs`).
2. CALLS of `_replace_query_graph` built here.  `self` is a `_Store`, the
   shim's GraphStore whose loader also RECORDS each call (method name,
   target graph, byte count): whether the region loads, and with which
   method, is part of what it decides.  Two `_Store`s are equal when the
   recorded loads are equal and every graph of the dataset (default graph
   and each named graph, by identifier) is isomorphic.

   0. the demo's first scenario (one stale triple, a neighbour named graph,
      a two-triple replacement);
   1. the demo's second scenario (empty replacement: clear, early return);
   2. a target holding several triples that differ by subject, predicate
      and object, a blank-node description and a language/typed literal --
      so a clear narrowed to one predicate, one subject or one object leaves
      something behind; neighbours sharing two of three terms with them (and
      one identical triple) in the default graph and in a second named
      graph, which must survive; a replacement that re-adds one old triple;
   3. the same target with an empty replacement: everything cleared,
      neighbours intact, no load;
   4. a target graph that does not exist yet (clear of nothing, then load).

The store is emulated (pyoxigraph is not in the venv).  Both sides issue the
very same store call -- `-{ ?s ?p ?o }` transpiles to
`remove_from(target, (?s, ?p, ?o))`, which calls
`target.remove((None, None, None))` -- so the equivalence does not depend on
the store; the emulation only has to give that call a context-scoped meaning,
as oxrdflib does for a `Dataset(store="Oxigraph", default_union=False)`
graph (graph_store.py:965).
"""
from pathlib import Path

from rdflib import Graph, URIRef

import context_shim
from rdfeval import harness
from rdfeval.harness import run_pair

EX = "http://example.org/"
_URI = URIRef(EX + "derived/inferred")
_OTHER = URIRef(EX + "derived/dependencies")


class _RecordingInner(context_shim._Inner):
    """The shim's loader, plus a log of the calls the region makes."""

    def __init__(self, dataset):
        super().__init__(dataset)
        self.calls = []

    def load(self, *, input, format, to_graph):
        self.calls.append(("load", to_graph.value, format, len(input)))
        super().load(input=input, format=format, to_graph=to_graph)

    def bulk_load(self, *, input, format, to_graph):
        self.calls.append(("bulk_load", to_graph.value, format, len(input)))
        context_shim._Inner.load(self, input=input, format=format,
                                 to_graph=to_graph)


class _Store(context_shim.GraphStore):
    def __init__(self, **graphs):
        super().__init__()
        qd = self.query_dataset
        qd.store._inner = _RecordingInner(qd._dataset)
        for name, ttl in graphs.items():
            target = (qd._dataset.default_context if name == "default"
                      else qd.graph({"target": _URI, "other": _OTHER}[name]))
            target.parse(data=ttl, format="turtle")

    def _snapshot(self):
        ds = self.query_dataset._dataset
        return {str(g.identifier): g for g in ds.contexts()} | {
            "<default>": ds.default_context}

    def __eq__(self, other):
        if not isinstance(other, _Store):
            return NotImplemented
        a, b = self._snapshot(), other._snapshot()
        nonempty = lambda s: {k for k, g in s.items() if len(g)}
        return (self.query_dataset.store._inner.calls
                == other.query_dataset.store._inner.calls
                and nonempty(a) == nonempty(b)
                and all(harness.graphs_isomorphic(a[k], b[k]) for k in nonempty(a)))

    def __repr__(self):
        return "_Store(%r)" % {k: len(g) for k, g in self._snapshot().items()}


_STALE = (f"@prefix ex: <{EX}> .\n"
          "ex:stale ex:p 1 ; ex:r \"x\"@en .\n"
          "ex:stale2 ex:q 5 .\n"
          "ex:other ex:p \"1\"^^<http://www.w3.org/2001/XMLSchema#string> .\n"
          "ex:stale ex:s [ ex:p 1 ; ex:q ex:stale2 ] .\n")
# share two of three terms with a target triple; one is identical
_NEIGHBOURS = (f"@prefix ex: <{EX}> .\n"
               "ex:stale ex:p 2 . ex:stale ex:q 1 . ex:keep ex:p 1 .\n"
               "ex:stale ex:p 1 .\n")
_FRESH = (f"@prefix ex: <{EX}> .\n"
          "ex:fresh ex:p 3 ; ex:q [ ex:p \"b\"@fr ] .\n"
          "ex:stale ex:p 1 .\n")


def _call(store, data):
    return ((store, Graph().parse(data=data, format="turtle"), _URI),
            {"label": "inferred data"})


CALLS = [
    lambda: _call(_Store(target=f"<{EX}stale> <{EX}p> 1 .",
                         other=f"<{EX}keep> <{EX}p> 2 ."),
                  f"<{EX}fresh> <{EX}p> 3 .<{EX}fresh> <{EX}q> 4 ."),
    lambda: _call(_Store(target=f"<{EX}stale> <{EX}p> 1 ."), ""),
    lambda: _call(_Store(target=_STALE, other=_NEIGHBOURS, default=_NEIGHBOURS),
                  _FRESH),
    lambda: _call(_Store(target=_STALE, other=_NEIGHBOURS, default=_NEIGHBOURS),
                  ""),
    lambda: _call(_Store(other=_NEIGHBOURS), _FRESH),
]


def _demo_diffs():
    """Module state of the demo harness the two files carry."""
    here = Path(__file__).resolve().parent
    ns_o, _ = harness._exec_python(here / "original.py")
    ns_t, _ = harness._exec_ldpy(here / "translated.ldpy")
    diffs = []
    for name in ("replaced_graph", "neighbour_graph", "cleared_graph"):
        if not harness.graphs_isomorphic(ns_o[name], ns_t[name]):
            diffs.append(f"demo {name}: graphs not isomorphic "
                         f"({len(ns_o[name])} vs {len(ns_t[name])} triples)")
    return diffs


_DEMO = _demo_diffs()
_emit = harness._emit


def _emit_with_demo(verdict):
    verdict["diffs"] = list(verdict.get("diffs") or []) + _DEMO
    verdict["equivalent"] = bool(verdict.get("equivalent")) and not _DEMO
    _emit(verdict)


harness._emit = _emit_with_demo

VERDICT = run_pair(
    __file__,
    entry="_replace_query_graph",
    calls=CALLS,
)

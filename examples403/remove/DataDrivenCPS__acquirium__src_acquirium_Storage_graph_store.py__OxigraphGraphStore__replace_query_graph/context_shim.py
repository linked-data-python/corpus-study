"""Context shim (see meta.json) for
DataDrivenCPS/acquirium@e3bffb4bed : src/acquirium/Storage/graph_store.py.

The region is a method: its graph is bound by `self.query_dataset`, and its
imports come from the package and from pyoxigraph (a Rust extension that is
not in the evaluation venv).  This module restores those bindings so the
region executes outside the package, identically for both representations.
It registers stand-ins under the names the region imports, so the region's
own import lines stay exactly as upstream; `driver.py` imports it first.

  * `acquirium.internals._log.timed_debug` -- copied verbatim from
    src/acquirium/internals/_log.py of the same commit (no dependency
    outside the standard library).
  * `pyoxigraph.NamedNode` / `pyoxigraph.RdfFormat` -- the two names the
    region uses: a named node is its IRI, and only `RdfFormat.N_TRIPLES` is
    referenced, whose value is the format the region serialises to.
  * `self.query_dataset` -- upstream an rdflib `Dataset` over the oxigraph
    store, whose `store._inner` is the pyoxigraph store.  Here an rdflib
    `Dataset` over the default store, with an `_inner` whose `load` /
    `bulk_load` parse the region's N-Triples into the named graph the region
    asks for.  That is what the oxigraph loader does to the dataset; nothing
    else about the store is used by the region.

No RDF logic of the region is reproduced here: the shim only carries the
bindings, and both representations get the same ones.
"""

from __future__ import annotations

import logging
import sys
import time
import types
from contextlib import contextmanager
from typing import Iterator

from rdflib import Dataset, URIRef


# --- acquirium.internals._log (verbatim from the source repository) --------

@contextmanager
def timed_debug(logger: logging.Logger, msg: str, *args) -> Iterator[None]:
    """DEBUG-log entry + exit (with elapsed ms) around a block.

    Skip the cost entirely when DEBUG isn't enabled.
    """
    if not logger.isEnabledFor(logging.DEBUG):
        yield
        return
    start = time.perf_counter()
    logger.debug("→ " + msg, *args)
    try:
        yield
    finally:
        logger.debug("← " + msg + " (%.1f ms)", *args, (time.perf_counter() - start) * 1000.0)


# --- pyoxigraph stand-in ---------------------------------------------------

class NamedNode:
    """A pyoxigraph named node: an IRI, readable back through `.value`."""

    def __init__(self, value: str) -> None:
        self.value = value


class RdfFormat:
    N_TRIPLES = "nt"


# --- the oxigraph-backed query dataset -------------------------------------

class _Inner:
    """The pyoxigraph store behind `Dataset.store._inner`, as the region uses
    it: load N-Triples into one named graph of the dataset."""

    def __init__(self, dataset: Dataset) -> None:
        self._dataset = dataset

    def load(self, *, input, format, to_graph) -> None:
        self._dataset.graph(URIRef(to_graph.value)).parse(data=input,
                                                          format=format)

    def bulk_load(self, *, input, format, to_graph) -> None:
        self.load(input=input, format=format, to_graph=to_graph)


class _Store:
    def __init__(self, dataset: Dataset) -> None:
        self._inner = _Inner(dataset)


class QueryDataset:
    """`self.query_dataset`: `graph(uri)` and `store._inner`, nothing else."""

    def __init__(self) -> None:
        self._dataset = Dataset()
        self.store = _Store(self._dataset)

    def graph(self, identifier):
        return self._dataset.graph(identifier)


class GraphStore:
    """`self`: an OxigraphGraphStore reduced to the attribute the region reads."""

    def __init__(self) -> None:
        self.query_dataset = QueryDataset()


# --- register the stand-ins under the names the region imports -------------

_ox = types.ModuleType("pyoxigraph")
_ox.NamedNode = NamedNode
_ox.RdfFormat = RdfFormat
sys.modules.setdefault("pyoxigraph", _ox)

_pkg = sys.modules.setdefault("acquirium", types.ModuleType("acquirium"))
_internals = sys.modules.setdefault("acquirium.internals",
                                    types.ModuleType("acquirium.internals"))
_log = sys.modules.setdefault("acquirium.internals._log",
                              types.ModuleType("acquirium.internals._log"))
_log.timed_debug = timed_debug
_internals._log = _log
_pkg.internals = _internals

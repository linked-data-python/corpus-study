"""Context shim for the cognitedata/neat region.

The real ``cognite.neat`` cannot be imported in the evaluation venv: it
requires the Cognite SDK (``cognite.client``), networkx, mixpanel,
openpyxl and oxrdflib, none of which are installed, and stubbing
``cognite.client`` is not enough because neat's pydantic models validate
against real SDK classes (``data_modeling.ContainerId`` and friends).
``NeatInstanceStore.from_oxi_local_store()`` additionally needs a live
Oxigraph store.

This module therefore provides a MINIMAL STAND-IN for the two names the
region uses.  Only the behaviour the region observes is reproduced, and it
is transcribed from the real code:

* ``NeatValueError`` -- cognite/neat/_v0/core/_issues/errors: a ValueError.
* ``NeatInstanceStore.from_oxi_local_store`` -- _instance.py:169-188,
  which builds the store over an rdflib ``Dataset`` (here a plain
  in-memory one instead of Oxigraph).
* ``NeatInstanceStore._add_triples`` -- _instance.py:311-325, which adds
  the triples to ``self.graph(named_graph)``.
* ``NeatInstanceStore.diff`` -- _instance.py:455-471; the two guards are
  copied verbatim, the body after them is never reached by this region.

Everything else of neat is absent.  The stand-in is imported IDENTICALLY
by original.py and translated.ldpy, so it cannot favour either side.

``last_store_triples()`` exposes what the most recently created store
holds, so that the demo harness at the end of both files can make the
region's writes observable to the driver (the region's own assertions only
observe named-graph existence).
"""

from rdflib import Dataset, Graph, URIRef

_LAST_STORE = None


class NeatValueError(ValueError):
    """Stand-in for cognite.neat._v0.core._issues.errors.NeatValueError."""


class NeatInstanceStore:
    """Stand-in for cognite.neat._v0.core._store.NeatInstanceStore."""

    def __init__(self, dataset: Dataset):
        self.dataset = dataset

    @classmethod
    def from_oxi_local_store(cls, storage_dir=None) -> "NeatInstanceStore":
        global _LAST_STORE
        _LAST_STORE = cls(Dataset())
        return _LAST_STORE

    @property
    def named_graphs(self) -> list:
        return [g.identifier for g in self.dataset.graphs()]

    def graph(self, named_graph: URIRef) -> Graph:
        return self.dataset.graph(named_graph)

    def _add_triples(self, triples, named_graph: URIRef,
                     batch_size: int = 10_000) -> None:
        graph = self.graph(named_graph)
        for triple in triples:
            graph.add(triple)

    def diff(self, current_named_graph: URIRef,
             new_named_graph: URIRef) -> None:
        if current_named_graph not in self.named_graphs:
            raise NeatValueError(
                f"Current named graph not found: {current_named_graph}")
        if new_named_graph not in self.named_graphs:
            raise NeatValueError(
                f"New named graph not found: {new_named_graph}")
        raise NotImplementedError(
            "the real diff body is never reached by this region")


def last_store_triples() -> Graph:
    """Every quad of the most recently created store, as a plain Graph.

    Subject/predicate/object plus the named graph, so that a mistranslated
    named-graph IRI is visible too.
    """
    graph = Graph()
    if _LAST_STORE is None:
        return graph
    for s, p, o, c in _LAST_STORE.dataset:
        graph.add((s, p, o))
        graph.add((c.identifier if hasattr(c, "identifier") else c,
                   URIRef("urn:rdfeval:contains"), s))
    return graph

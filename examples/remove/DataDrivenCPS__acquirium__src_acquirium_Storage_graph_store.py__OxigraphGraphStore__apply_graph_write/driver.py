"""Validation driver for OxigraphGraphStore._apply_graph_write.

The region empties a target graph, copies an incoming one into it and
propagates the incoming prefix bindings.  It is a method, so each fixture
passes a stand-in `self` holding a fresh query Dataset; the stand-in compares
by the prefixes bound on that dataset, which is the only effect of the region
that graph isomorphism cannot see.

Three calls:
  replace=True   the wildcard remove has work to do (the target is not empty)
  replace=False  the target keeps what it had and the incoming is merged in
  replace=True with an empty incoming — the target ends up empty, which is the
                 case a mistranslated wildcard would get wrong in the other
                 direction

Added by the repair audit (2026-10-31): the target in the shape the
repository gives it.  `insert_graph` passes
`self._registered_data_graph(graph_uri)` (graph_store.py:897), that is
`self.source_dataset.graph(target_uri)` (graph_store.py:669): ONE named graph
of a `Dataset(store="Oxigraph", default_union=False)` (graph_store.py:965)
that also holds the other source graphs and a default graph.  A standalone
`Graph` as target cannot tell a clear of that one graph from a clear of the
whole store.  `_DatasetStore` emulates the source dataset with an in-memory
store (pyoxigraph is not in the venv) that RECORDS every `remove` it receives
(pattern and context): whether the region clears through one store call
scoped to the target context is part of what it decides.  Two
`_DatasetStore`s are equal when their remove logs are equal, every graph of
the source dataset (default graph and each named graph, by identifier) is
isomorphic, and the prefixes bound on the source dataset (where
`target.bind` lands) and on the query dataset are the same.  The
`acquirium.graph_store` debug log is captured per call and compared too.

  3. replace=True: the target holds triples that differ by subject,
     predicate and object, and a blank-node description (its triples must
     all go, leaving no orphan); the default graph and a second source graph
     hold neighbours sharing two of three terms with them, and one identical
     triple -- all must survive.
  4. replace=False on the same dataset: nothing removed, nothing logged.
  5. replace=True, empty incoming: target emptied, neighbours intact.
  6. replace=True on a target graph that does not exist yet.
  7. replace=True with an incoming that binds `ex:` while the query and
     source datasets already bind `ex:` to another namespace and the incoming
     namespace to another prefix (`exo:`): what `override=False` keeps.
"""
import logging

from rdflib import Dataset, Graph, URIRef
from rdflib.plugins.stores.memory import Memory

from rdfeval import harness
from rdfeval.harness import run_pair

INCOMING = """
@prefix ex:   <http://example.org/> .
@prefix unit: <http://qudt.org/vocab/unit/> .

ex:sensor1 a ex:Sensor ; ex:unit unit:DEG_C ; ex:label "one" .
ex:sensor2 a ex:Sensor ; ex:unit unit:PERCENT .
"""

EXISTING = """
@prefix ex:  <http://example.org/> .
@prefix old: <http://example.org/old/> .

ex:sensor1 ex:label "stale" .
old:gone a old:Thing .
"""


class Store:
    """Stand-in for the enclosing OxigraphGraphStore: the region reads only
    `self.query_dataset`, on whose namespace manager it binds prefixes."""

    def __init__(self):
        self.query_dataset = Dataset()

    def _prefixes(self):
        return sorted((p, str(n)) for p, n in self.query_dataset.namespaces())

    def __eq__(self, other):
        return isinstance(other, Store) and self._prefixes() == other._prefixes()

    def __hash__(self):
        return 0


def _graph(ttl):
    return Graph().parse(data=ttl, format="turtle") if ttl else Graph()


def call(incoming_ttl, existing_ttl, replace):
    return lambda: ((Store(), _graph(incoming_ttl)),
                    {"target": _graph(existing_ttl), "replace": replace})


# --- the repository's shape: one named graph of the source dataset ---------

EX = "http://example.org/"
MAIN = URIRef(EX + "graph/main")          # the target source graph
SIBLING = URIRef(EX + "graph/source/s1")  # another registered source graph

TARGET_TTL = """
@prefix ex:  <http://example.org/> .
@prefix old: <http://example.org/old/> .
ex:sensor1 ex:label "stale" ; ex:unit ex:K .
ex:sensor3 ex:label "three"@en .
old:gone a old:Thing ; ex:loc [ ex:x 1 ; ex:y [ ex:z "deep" ] ] .
"""

# share two of three terms with a target triple; the last one is identical
NEIGHBOURS_TTL = """
@prefix ex:  <http://example.org/> .
@prefix old: <http://example.org/old/> .
ex:sensor1 ex:label "fresh" .
ex:sensor1 ex:name "stale" .
ex:sensor9 ex:label "stale" .
old:gone a old:Other .
ex:sensor3 ex:label "three"@fr .
ex:sensor1 ex:label "stale" .
"""


class _RecordingMemory(Memory):
    """In-memory store that logs each remove it is asked for."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.removes = []

    def remove(self, triple, context=None):
        ctx = None if context is None else str(context.identifier)
        self.removes.append((triple, ctx))
        super().remove(triple, context)


class _DatasetStore:
    """Stand-in for OxigraphGraphStore with its two datasets."""

    def __init__(self, target_ttl, neighbours_ttl, bind_ex_elsewhere=False):
        self.source_dataset = Dataset(store=_RecordingMemory(), default_union=False)
        self.query_dataset = Dataset()
        if target_ttl:
            self.source_dataset.graph(MAIN).parse(data=target_ttl, format="turtle")
        if neighbours_ttl:
            self.source_dataset.default_context.parse(data=neighbours_ttl, format="turtle")
            self.source_dataset.graph(SIBLING).parse(data=neighbours_ttl, format="turtle")
        if bind_ex_elsewhere:
            # after the parses, which bind `ex:` themselves: the incoming
            # namespace under another prefix, its prefix on another namespace
            for ds in (self.source_dataset, self.query_dataset):
                ds.bind("exo", EX, override=True)
                ds.bind("ex", "http://elsewhere.example/", override=True, replace=True)
        self.source_dataset.store.removes.clear()

    def target(self):
        """`_registered_data_graph(None)`: graph_store.py:664-669."""
        return self.source_dataset.graph(MAIN)

    def _snapshot(self):
        ds = self.source_dataset
        return {str(g.identifier): g for g in ds.contexts() if len(g)} | {
            "<default>": ds.default_context}

    @staticmethod
    def _bound(ds):
        return sorted((p, str(n)) for p, n in ds.namespaces())

    def _key(self):
        return (self.source_dataset.store.removes,
                self._bound(self.source_dataset), self._bound(self.query_dataset))

    def __eq__(self, other):
        if not isinstance(other, _DatasetStore):
            return NotImplemented
        a, b = self._snapshot(), other._snapshot()
        return (self._key() == other._key() and set(a) == set(b)
                and all(harness.graphs_isomorphic(a[k], b[k]) for k in a))

    def __hash__(self):
        return 0

    def __repr__(self):
        return "_DatasetStore(%r, removes=%r)" % (
            {k: len(g) for k, g in self._snapshot().items()},
            self.source_dataset.store.removes)


class _LogCapture(logging.Handler):
    def __init__(self):
        super().__init__(logging.DEBUG)
        self.records = []

    def emit(self, record):
        self.records.append((record.levelname, record.getMessage()))


def dataset_call(incoming_ttl, target_ttl, replace, bind_ex_elsewhere=False):
    def make():
        store = _DatasetStore(target_ttl, NEIGHBOURS_TTL, bind_ex_elsewhere)
        return ((store, _graph(incoming_ttl)),
                {"target": store.target(), "replace": replace})
    return make


CALLS = [
    call(INCOMING, EXISTING, True),
    call(INCOMING, EXISTING, False),
    call(None, EXISTING, True),
    dataset_call(INCOMING, TARGET_TTL, True),
    dataset_call(INCOMING, TARGET_TTL, False),
    dataset_call(None, TARGET_TTL, True),
    dataset_call(INCOMING, None, True),
    dataset_call(INCOMING, TARGET_TTL, True, bind_ex_elsewhere=True),
]


def _log_diffs():
    """The `acquirium.graph_store` records of each call, on both sides.

    Run apart from `run_pair` (which does not capture logging) and folded
    into its verdict.  The `except` branch is not reached by these inputs --
    an in-memory store's `bind` does not raise -- so equal records here say
    that neither side logs where the other does not.
    """
    from pathlib import Path
    here = Path(__file__).resolve().parent
    ns_o, _ = harness._exec_python(here / "original.py")
    ns_t, _ = harness._exec_ldpy(here / "translated.ldpy")
    logger = logging.getLogger("acquirium.graph_store")
    level = logger.level
    logger.setLevel(logging.DEBUG)
    diffs = []
    try:
        for i, make in enumerate(CALLS):
            records = []
            for ns in (ns_o, ns_t):
                (store, incoming), kwargs = make()
                handler = _LogCapture()
                logger.addHandler(handler)
                try:
                    ns["_apply_graph_write"](store, incoming, **kwargs)
                finally:
                    logger.removeHandler(handler)
                records.append(handler.records)
            if records[0] != records[1]:
                diffs.append(f"call[{i}]: log records differ "
                             f"({records[0]!r} vs {records[1]!r})")
    finally:
        logger.setLevel(level)
    return diffs


_LOGS = _log_diffs()
_emit = harness._emit


def _emit_with_logs(verdict):
    verdict["diffs"] = list(verdict.get("diffs") or []) + _LOGS
    verdict["equivalent"] = bool(verdict.get("equivalent")) and not _LOGS
    _emit(verdict)


harness._emit = _emit_with_logs

VERDICT = run_pair(
    __file__,
    entry='_apply_graph_write',
    calls=CALLS,
)

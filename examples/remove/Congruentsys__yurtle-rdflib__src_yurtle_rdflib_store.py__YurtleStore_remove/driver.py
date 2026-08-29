"""Validation driver for YurtleStore.remove.

The region is rdflib's *Store* `remove`, not a call to `Graph.remove`: the
pattern arrives as a value, `(s, p, o)` with `None` for a wildcard, and the
method resolves it against the store's own `internal_graph` before deleting
the matches one by one.  Only that inner, fully-bound deletion is an island;
see meta.json.

`self` is a stand-in for the enclosing store, with the five members the region
reads.  `_resolve_file_for_subject`, `_uri_to_path` and `_mark_file_dirty` are
the upstream bodies; `flush` keeps the observable part of the upstream one (it
clears the dirty set and returns a count) without touching the filesystem.
The stand-in compares by internal graph (isomorphism), dirty set and flush
count — everything the region can change.

The seven calls walk the wildcard shapes a store sees: `(s, p, None)`, a
fully-bound triple, `(None, p, None)`, the same one-wildcard pattern with
auto_flush on (so flush() runs), `(s, None, None)` on a subject with no
provenance (nothing is dirtied), `(None, None, o)` and a pattern that matches
nothing.  `(None, None, None)` is deliberately NOT among them: the region
resolves each match's file AFTER deleting it, so a full wipe makes the set of
dirtied files depend on the store's iteration order, which rdflib does not
promise (observed varying from run to run).  That is the region's own
fragility, not the translation's, and a driver must not make a verdict rest
on it.
"""
from pathlib import Path

from rdflib import Graph, Namespace, URIRef
from rdflib.compare import isomorphic

from rdfeval.harness import run_pair

PROVENANCE = Namespace("https://yurtle.dev/provenance/")
EX = Namespace("http://example.org/")

DATA = """
@prefix ex:   <http://example.org/> .
@prefix prov: <https://yurtle.dev/provenance/> .

ex:alice a ex:Person ;
    ex:name "Alice" ;
    ex:knows ex:bob, ex:carol ;
    prov:definedIn <file:///w/alice.md> .

ex:bob a ex:Person ;
    ex:name "Bob" ;
    prov:definedIn <file:///w/bob.md> .

# no provenance: _resolve_file_for_subject returns None and nothing is dirtied
ex:carol a ex:Person ;
    ex:name "Carol" .
"""


class Store:
    """Stand-in for YurtleStore: the members `remove` reads, upstream bodies."""

    def __init__(self, auto_flush=False):
        self.internal_graph = Graph().parse(data=DATA, format="turtle")
        self.auto_flush = auto_flush
        self._dirty_files: set[Path] = set()
        self.file_states: dict = {}
        self.flush_calls = 0

    def _uri_to_path(self, uri: URIRef):
        """Convert a file:// URI back to a Path."""
        uri_str = str(uri)
        if uri_str.startswith("file://"):
            return Path(uri_str[7:])
        return None

    def _resolve_file_for_subject(self, subject: URIRef):
        for file_uri in self.internal_graph.objects(subject, PROVENANCE.definedIn):
            if not isinstance(file_uri, URIRef):
                continue
            path = self._uri_to_path(file_uri)
            if path:
                return path
        return None

    def _mark_file_dirty(self, path: Path) -> None:
        self._dirty_files.add(path)
        if path in self.file_states:
            self.file_states[path].is_dirty = True

    def flush(self) -> int:
        # the observable part of the upstream flush(), without the file I/O
        if not self._dirty_files:
            return 0
        self.flush_calls += 1
        flushed = len(self._dirty_files)
        self._dirty_files.clear()
        return flushed

    def __eq__(self, other):
        return (isinstance(other, Store)
                and isomorphic(self.internal_graph, other.internal_graph)
                and sorted(map(str, self._dirty_files))
                == sorted(map(str, other._dirty_files))
                and self.flush_calls == other.flush_calls)

    def __hash__(self):
        return 0


def call(pattern, auto_flush=False):
    return lambda: ((Store(auto_flush=auto_flush), pattern), {})


VERDICT = run_pair(
    __file__,
    entry='remove',
    calls=[
        call((EX.alice, EX.name, None)),          # one wildcard, one match
        call((EX.alice, EX.knows, EX.bob)),       # fully bound
        call((None, EX.name, None)),              # two wildcards, three matches
        call((EX.alice, EX.name, None), auto_flush=True),  # flush() runs
        call((EX.carol, None, None)),             # subject wipe, no provenance
        call((None, None, EX.bob)),               # wildcards in the first two
        call((EX.nobody, EX.name, None)),         # no match at all
    ],
)

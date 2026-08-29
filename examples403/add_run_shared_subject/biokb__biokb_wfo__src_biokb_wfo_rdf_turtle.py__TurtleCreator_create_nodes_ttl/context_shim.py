# Context shim (see meta.json): minimal stand-ins for the biokb_wfo
# dependencies TurtleCreator.create_nodes_ttl needs to execute outside the
# package (biokb/biokb_wfo@67fc2c53662d1fe46df1accb6423401e88cb9e1c,
# src/biokb_wfo/rdf/turtle.py, src/biokb_wfo/db/models.py,
# src/biokb_wfo/rdf/namespaces.py, src/biokb_wfo/constants.py) -- none of
# biokb_wfo, tqdm or a real database is installed in this environment.
#
# get_empty_graph is the region's own helper (present in the real
# rdf/turtle.py, just above the extracted lines): it returns a fresh
# rdflib.Graph. It also stashes the graph it built onto the caller's local
# `self` (found via the call stack -- get_empty_graph() is called bare, not
# as self.get_empty_graph(), so there is no other channel back) because
# create_nodes_ttl's own return value is only a file path: comparing that
# alone would be a hollow green (the path string is the same whether or not
# the graph got a single triple right) -- see driver.py.
#
# TurtleCreator is reduced to what the region reads/calls:
# self.__ttls_folder (the region is extracted at module level, outside any
# `class` statement, so the name is never mangled -- Python only mangles
# `self.__x` lexically inside a class body) and self.Session() as a context
# manager yielding a query-builder object. models.Name is reduced to six
# attributes exposing the SQLAlchemy filter methods (.isnot, .in_, ==) the
# region chains through .where(...) -- the fake session below ignores every
# filter value it is handed, so what they return does not matter, only that
# calling them does not raise.
#
# tqdm is not installed either: the real function is a transparent
# progress-bar wrapper around its iterable argument, so an identity
# pass-through preserves the region's meaning exactly.
import sys
from types import SimpleNamespace

from rdflib import Graph, Namespace
from rdflib.compare import to_isomorphic

BASIC_NODE_LABEL = "Taxon"
DB_DEFAULT_CONNECTION_STR = "sqlite:///:memory:"  # unused by the region
EXPORT_FOLDER = "/tmp/biokb_wfo_export"           # unused by the region


def get_empty_graph() -> Graph:
    g = Graph()
    caller_self = sys._getframe(1).f_locals.get("self")
    if caller_self is not None:
        caller_self.produced_graph = g
    return g


def tqdm(iterable, *args, **kwargs):
    return iterable


class _Col:
    """Stand-in for a SQLAlchemy InstrumentedAttribute: the region only
    chains .where(...) filters through it, and the fake session below
    (_FakeQuery.where) ignores every filter value -- so what these return
    does not matter, only that calling them does not raise."""

    def __eq__(self, other):
        return True

    def isnot(self, other):
        return True

    def in_(self, other):
        return True


class _Name:
    id = _Col()
    full_name = _Col()
    rank = _Col()
    parent_id = _Col()
    ipni = _Col()
    role = _Col()
    status = _Col()


models = SimpleNamespace(Name=_Name)

namespaces = SimpleNamespace(
    WFO_NS=Namespace("http://example.org/wfo/"),
    NODE_NS=Namespace("http://example.org/node/"),
    REL_NS=Namespace("http://example.org/rel/"),
    IPNI_NS=Namespace("http://example.org/ipni/"),
)


class _FakeQuery:
    def __init__(self, rows):
        self._rows = rows

    def query(self, *cols):
        return self

    def where(self, *conds):
        return self

    def all(self):
        return self._rows


class _FakeSession:
    """Stand-in for `with self.Session() as session:` -- no real database:
    the rows a case wants are captured when the TurtleCreator stand-in
    below is built, and handed back verbatim by .all()."""

    def __init__(self, rows):
        self._rows = rows

    def __enter__(self):
        return _FakeQuery(self._rows)

    def __exit__(self, *exc):
        return False


class TurtleCreator:
    """Minimal stand-in for biokb_wfo.rdf.turtle.TurtleCreator.
    produced_graph is not part of the real class: it is how
    get_empty_graph (above) hands the driver the graph the region built,
    since create_nodes_ttl itself only returns a file path (see
    driver.py)."""

    def __init__(self, ttls_folder, rows):
        setattr(self, "__ttls_folder", ttls_folder)
        self.Session = lambda: _FakeSession(rows)
        self.produced_graph = None

    def __eq__(self, other):
        if not isinstance(other, TurtleCreator):
            return NotImplemented
        if self.produced_graph is None or other.produced_graph is None:
            return self.produced_graph is other.produced_graph
        return to_isomorphic(self.produced_graph) == to_isomorphic(other.produced_graph)

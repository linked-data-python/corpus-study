"""Validation driver for
statnett__KGraphPy__tests_test_header.py__test_repair_blank_header_subject_dctidentifier.

Establishes semantic equivalence of original.py and translated.ldpy.

The extracted test takes `header_type` (a real pytest.mark.parametrize
argument) and `caplog` (a pytest fixture) as parameters. `run_pair` has no
pytest session behind it, so `caplog` is stood in for by `_FakeCaplog`
below.

`run_pair` builds BOTH sides' (args, kwargs) before calling either side
(`case()` is invoked once for the original call and once for the translated
call, back to back, then `fo(...)` runs and only afterwards `ft(...)`), so a
`_FakeCaplog` cannot know at construction time where "its" window into the
log starts — the other side's call has not happened yet, but by the time
its `.messages` is *read* (synchronously, inside the corresponding call,
right after the from_graph() call it wraps and before the next call
starts), every record logged so far is unambiguously either "mine" or
"already consumed by the previous read". So capture is a single handler
shared by every `_FakeCaplog`, appending to one list, and each instance's
`.messages` returns everything logged since the last time ANY `_FakeCaplog`
read it. That tracks the real per-call read order (fo's read happens before
ft's call even starts), not the construction order.

Mutation audit of 2026-10-30.  The region's own assertions only look at
`header.subject` and the log, and `_FakeCaplog` compared equal to any other
instance, so the graph the `+{ }` island builds went unobserved: a type
hard-wired to dcat:Dataset, `"1234"` written as an integer, a typed or
tagged literal, an extra triple on `b`, a rebound dcterms prefix, and the
decorator's parametrize list changed all stayed green.  Now, identically
on both sides:

  * `CIMMetadataHeader.from_graph` (the vendored real body, unchanged) is
    wrapped by a recorder that logs, per call, the input graph `g` (triples
    in N3, its one blank node under a fixed label, since `b` is a fresh
    `BNode()`) and its prefix bindings, then the header it returns: subject,
    header graph triples and the header graph's bindings (which
    `collect_specific_namespaces` derives from `g`'s bindings, and which the
    repository's other tests read, test_header.py:663);
  * each `_FakeCaplog` keeps what it read -- the log messages, the
    recorder's entries since the previous read, and the
    `pytest.mark.parametrize` marks of the test function that read it
    (found through the calling frame) -- and two instances are equal only
    when they read the same thing.  `run_pair` compares the `caplog`
    kwarg after the call, so this is where the two sides meet.
"""
import logging
import re
import sys

from rdflib import BNode
from rdflib.namespace import DCAT
from kgraphpy.namespaces import MD
from kgraphpy.header import CIMMetadataHeader
from rdfeval.harness import run_pair

_LOG: list[str] = []
_CURSOR = [0]
_OBS: list[tuple] = []
_OBS_CURSOR = [0]
_BNODE_ID = re.compile(r"\bN[0-9a-f]{32}\b")


def _n3(term):
    return "_:b" if isinstance(term, BNode) else term.n3()


def _triples(graph):
    return sorted(tuple(_n3(t) for t in triple) for triple in graph)


def _bindings(graph):
    return sorted((prefix, str(ns)) for prefix, ns in graph.namespaces())


_from_graph = CIMMetadataHeader.from_graph.__func__


def _recording_from_graph(cls, graph, metadata_objects=None):
    entry = ("from_graph", _triples(graph), _bindings(graph))
    header = _from_graph(cls, graph, metadata_objects)
    _OBS.append(entry + (header.subject, _triples(header.graph),
                         _bindings(header.graph)))
    return header


CIMMetadataHeader.from_graph = classmethod(_recording_from_graph)


class _LogSink(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        _LOG.append(record.getMessage())


_root = logging.getLogger()
if not any(isinstance(h, _LogSink) for h in _root.handlers):
    _root.addHandler(_LogSink())
_root.setLevel(logging.WARNING)


class _FakeCaplog:
    """Stand-in for pytest's `caplog` fixture: `.messages` is the list of
    messages logged (anywhere) since the previous read, mirroring what a
    real per-test `caplog.messages` would show for the log records emitted
    during this one call."""

    def __init__(self) -> None:
        self.seen: list = []

    @property
    def messages(self) -> list[str]:
        result = _LOG[_CURSOR[0]:]
        _CURSOR[0] = len(_LOG)
        observed = _OBS[_OBS_CURSOR[0]:]
        _OBS_CURSOR[0] = len(_OBS)
        caller = sys._getframe(1)
        test = caller.f_globals.get(caller.f_code.co_name)
        marks = [(m.name, m.args) for m in getattr(test, "pytestmark", [])]
        # the first message names the fresh blank node: fixed label
        logged = [_BNODE_ID.sub("_:b", m) for m in result]
        self.seen.append((logged, observed, marks))
        return result

    # run_pair compares every kwarg between the original and translated
    # call, after the call: two stand-ins are equal when their test read
    # the same log messages, the same from_graph records and the same
    # parametrize marks (see the module docstring).
    def __eq__(self, other) -> bool:
        return isinstance(other, _FakeCaplog) and self.seen == other.seen

    def __repr__(self) -> str:
        return f"_FakeCaplog({self.seen!r})"


def _case(header_type):
    return lambda: ((header_type,), {"caplog": _FakeCaplog()})


VERDICT = run_pair(
    __file__,
    entry='test_repair_blank_header_subject_dctidentifier',
    calls=[_case(MD.FullModel), _case(DCAT.Dataset)],
)

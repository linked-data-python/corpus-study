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
"""
import logging

from rdflib.namespace import DCAT
from kgraphpy.namespaces import MD
from rdfeval.harness import run_pair

_LOG: list[str] = []
_CURSOR = [0]


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

    @property
    def messages(self) -> list[str]:
        result = _LOG[_CURSOR[0]:]
        _CURSOR[0] = len(_LOG)
        return result

    # run_pair compares every kwarg between the original and translated
    # call; this stand-in carries no state of its own to compare (the real
    # oracle is the region's own assertions over `.messages`), so make it
    # trivially equal to any other instance rather than fail on identity.
    def __eq__(self, other) -> bool:
        return isinstance(other, _FakeCaplog)

    def __repr__(self) -> str:
        return "_FakeCaplog()"


def _case(header_type):
    return lambda: ((header_type,), {"caplog": _FakeCaplog()})


VERDICT = run_pair(
    __file__,
    entry='test_repair_blank_header_subject_dctidentifier',
    calls=[_case(MD.FullModel), _case(DCAT.Dataset)],
)

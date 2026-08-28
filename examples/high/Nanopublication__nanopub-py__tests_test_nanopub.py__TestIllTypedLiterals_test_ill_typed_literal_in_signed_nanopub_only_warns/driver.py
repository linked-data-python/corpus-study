"""Validation driver: the region is a pytest method taking the `caplog` fixture.

pytest is not driving the run, so the driver supplies a minimal stand-in for
`caplog` (``at_level`` + ``.text``).  Its ``__eq__`` compares the captured log
text, which makes the harness check that both sides emitted the same warning
about the ill-typed literal.
"""
import contextlib
import logging

from rdfeval.harness import run_pair


class _CaplogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.lines = []

    def emit(self, record):
        self.lines.append(self.format(record))


class Caplog:
    """Minimal stand-in for pytest's caplog fixture."""

    def __init__(self):
        self.handler = _CaplogHandler()

    @contextlib.contextmanager
    def at_level(self, level, logger=None):
        lg = logging.getLogger(logger)
        previous = lg.level
        lg.setLevel(level)
        lg.addHandler(self.handler)
        try:
            yield self
        finally:
            lg.removeHandler(self.handler)
            lg.setLevel(previous)

    @property
    def text(self):
        return "\n".join(self.handler.lines)

    def __eq__(self, other):
        return isinstance(other, Caplog) and self.text == other.text

    def __repr__(self):
        return f"Caplog({self.text!r})"


VERDICT = run_pair(__file__,
                   entry="test_ill_typed_literal_in_signed_nanopub_only_warns",
                   calls=[lambda: ((None, Caplog()), {})])

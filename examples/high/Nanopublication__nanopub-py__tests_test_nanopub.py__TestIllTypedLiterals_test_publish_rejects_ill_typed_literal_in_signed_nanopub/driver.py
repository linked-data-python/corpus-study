"""Validation driver: publishing a signed nanopub that carries an ill-typed
literal must raise instead of reaching the network.

The `nanopub` package is not installed in the evaluation venv; it is taken
from the corpus checkout by appending it to sys.path (appended, not
prepended, so the example's own `tests` shim package keeps priority over the
corpus one).  The region takes pytest's `monkeypatch` fixture, which the
driver instantiates directly; `self` is unused.

The equivalence evidence is the region's own `pytest.raises(...,
match="not-a-number")`: the error is raised, with that message, only if the
triple added to the pubinfo graph really carries "not-a-number" typed as
xsd:integer.
"""
import sys
from pathlib import Path

_CORPUS = (Path(__file__).resolve().parents[3]
           / "corpus" / "repos" / "Nanopublication__nanopub-py")
if str(_CORPUS) not in sys.path:
    sys.path.append(str(_CORPUS))

from rdfeval.harness import run_pair  # noqa: E402


class _RecordingMonkeyPatch:
    """Stand-in for pytest's `monkeypatch` fixture, comparable by value.

    The region only ever calls `.setattr`; pytest's own MonkeyPatch objects
    compare by identity, which would make the harness report a spurious
    difference between the two sides.  Like the real fixture used here,
    nothing is undone: the region deliberately leaves `is_valid` patched.
    """

    def __init__(self):
        self.calls = []

    def setattr(self, target, name, value):
        self.calls.append((getattr(target, "__name__", repr(target)), name))
        setattr(target, name, value)

    def __eq__(self, other):
        if not isinstance(other, _RecordingMonkeyPatch):
            return NotImplemented
        return self.calls == other.calls


def with_monkeypatch():
    return ((None, _RecordingMonkeyPatch()), {})


VERDICT = run_pair(
    __file__,
    entry="test_publish_rejects_ill_typed_literal_in_signed_nanopub",
    calls=[with_monkeypatch],
)

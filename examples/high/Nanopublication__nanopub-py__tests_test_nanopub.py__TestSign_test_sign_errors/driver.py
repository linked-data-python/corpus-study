"""Validation driver for TestSign.test_sign_errors.

Context (identical for both representations):

* the ``nanopub`` package is not installed in the evaluation venv, so the
  corpus checkout Nanopublication/nanopub-py@05022dc4bc is put on sys.path
  before either module is executed;
* ``tests.conftest`` is replaced by the local ``conftest_context.py`` shim
  (see its header): the RSA key pair the profile needs was copied from
  Nanopublication/nanopub-testsuite@main instead of being downloaded.

The region is a pytest test taking ``self`` (unused) and the ``monkeypatch``
fixture, for which pytest's public ``MonkeyPatch`` is used.  It returns
nothing; its three ``pytest.raises`` blocks are the behavioural check, and
they only hold if the three sub-graphs were populated the same way on both
sides (an empty assertion, provenance or pubinfo makes ``sign()`` raise a
different error).
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE.parents[2] / "corpus" / "repos" / "Nanopublication__nanopub-py"
if str(CORPUS) not in sys.path:
    sys.path.insert(0, str(CORPUS))

import pytest  # noqa: E402

from rdfeval.harness import run_pair  # noqa: E402


_LIVE = []


class _ComparableMonkeyPatch(pytest.MonkeyPatch):
    """pytest's public MonkeyPatch, with two harness accommodations.

    * ``__eq__`` by type, so the harness can compare the two runs' arguments.
    * ``setattr`` first undoes the patch left by the previous run.  The
      harness builds both fixtures before calling either side, so the
      original's patch of ``Nanopub.is_valid`` would otherwise still be in
      place while the translated side runs.  That would in fact be harmless
      here — ``Nanopub.sign()`` raises on the missing profile (source line
      228) and on the existing signature (line 230) before it ever reads
      ``is_valid`` (line 233) — but the runs are kept independent anyway.
    """

    def setattr(self, *args, **kwargs):
        while _LIVE:
            _LIVE.pop().undo()
        _LIVE.append(self)
        return super().setattr(*args, **kwargs)

    def __eq__(self, other):
        return isinstance(other, _ComparableMonkeyPatch)


def with_monkeypatch():
    return ((None, _ComparableMonkeyPatch()), {})


VERDICT = run_pair(__file__, entry="test_sign_errors", calls=[with_monkeypatch])

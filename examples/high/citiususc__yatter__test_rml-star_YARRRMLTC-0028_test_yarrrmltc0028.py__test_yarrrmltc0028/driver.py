"""Validation driver for yatter's YARRRMLTC-0028 test.

Context (identical for both representations):

* ``yatter`` is not installed in the evaluation venv, so the corpus checkout
  citiususc/yatter@0b40dff623 (its ``src/`` directory) is put on sys.path
  before either module is executed;
* ``coloredlogs``, which yatter imports only to colourise its logger, is not
  installed either and is replaced by a no-op stub module;
* the region reads ``mapping.ttl`` and ``mapping.yml`` next to its own
  ``__file__``; both files (1.3 KB / 0.4 KB) were copied from
  test/rml-star/YARRRMLTC-0028/ of the same checkout into this directory, so
  both original.py and translated.ldpy find them.

The region takes no argument and returns nothing: it asserts that the
mapping yatter generates from the YARRRML source is isomorphic to the
expected RML graph.
"""
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
YATTER_SRC = HERE.parents[2] / "corpus" / "repos" / "citiususc__yatter" / "src"
if str(YATTER_SRC) not in sys.path:
    sys.path.insert(0, str(YATTER_SRC))
if "coloredlogs" not in sys.modules:
    _stub = types.ModuleType("coloredlogs")
    _stub.install = lambda *args, **kwargs: None
    sys.modules["coloredlogs"] = _stub

from rdfeval.harness import run_pair  # noqa: E402


def no_args():
    return ((), {})


VERDICT = run_pair(__file__, entry="test_yarrrmltc0028", calls=[no_args])

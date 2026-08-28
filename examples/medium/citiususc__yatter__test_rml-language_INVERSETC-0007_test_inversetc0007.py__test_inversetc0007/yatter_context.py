"""Context shim for the citiususc/yatter region.

Two absent packages:

* ``yatter`` itself is not installed, but it imports cleanly from the
  corpus checkout once ``coloredlogs`` (a logging-cosmetics dependency,
  also absent) is stubbed out; importing this module does both.  The real
  ``yatter.inverse_translation`` is what the region calls.

* ``DeepDiff`` (the test-only dependency of yatter) is not installed.
  ``DeepDiff`` below is a MINIMAL STAND-IN: the region uses it only as
  ``DeepDiff(expected, actual, ignore_order=True)`` and then tests the
  result for truthiness, so an order-insensitive deep comparison
  returning ``{}`` when the two structures match is behaviourally
  sufficient.  (Checked: for this fixture the two ``mappings`` dicts are
  in fact exactly equal, so no ordering subtlety is being papered over.)

``mapping.ttl`` and ``mapping.yml`` are copied verbatim next to this file
from the corpus checkout, so the region's
``os.path.dirname(os.path.realpath(__file__))`` lookups resolve unchanged.

This module is imported IDENTICALLY by original.py and translated.ldpy.
"""

import sys
import types

_CHECKOUT = ("/home/lefrancois/Documents/recherche/semantic_web_micropython"
             "/github/corpus/repos/citiususc__yatter/src")


class _InertModule(types.ModuleType):
    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return type(name, (), {"__init__": lambda self, *a, **k: None,
                               "__call__": lambda self, *a, **k: None})


if "coloredlogs" not in sys.modules:
    _cl = _InertModule("coloredlogs")
    _cl.__path__ = []
    sys.modules["coloredlogs"] = _cl

if _CHECKOUT not in sys.path:
    sys.path.insert(0, _CHECKOUT)


def _canon(value):
    """Order-insensitive canonical string form of a nested structure."""
    if isinstance(value, dict):
        return "{" + ",".join(sorted(f"{_canon(k)}:{_canon(v)}"
                                     for k, v in value.items())) + "}"
    if isinstance(value, (list, tuple, set, frozenset)):
        return "[" + ",".join(sorted(_canon(v) for v in value)) + "]"
    return repr(value)


def DeepDiff(t1, t2, ignore_order=False, **kwargs):
    """Stand-in for deepdiff.DeepDiff, order-insensitive only."""
    if not ignore_order:
        raise NotImplementedError(
            "this stand-in only implements ignore_order=True")
    if _canon(t1) == _canon(t2):
        return {}
    return {"values_changed": {"root": {"old_value": t1, "new_value": t2}}}

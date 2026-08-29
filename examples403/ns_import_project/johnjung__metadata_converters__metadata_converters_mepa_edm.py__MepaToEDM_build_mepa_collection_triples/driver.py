"""Validation driver for
johnjung__metadata_converters__metadata_converters_mepa_edm.py__MepaToEDM_build_mepa_collection_triples.

`demo()` (identical on both sides, appended after the extracted region --
see meta.json) calls the classmethod's own wrapped function directly against
a real MepaStub instance and returns the resulting graph: `run_pair`'s
generic ``entry=``/``calls=`` path already special-cases a returned
``rdflib.Graph`` as isomorphism, which is exactly this region's oracle (it
only ever adds triples).

The region computes `now = Literal(datetime.datetime.utcnow(), datatype=...)`
and passes it to `self.rem_graph`, which stores it as `dcterms:modified` --
a live wall-clock value that would make the two sides' graphs non-isomorphic
by construction (two separate calls, microseconds apart, to the real
`utcnow()`), for a reason that has nothing to do with whether the
translation is correct. `datetime.datetime` is frozen for the duration of
`run_pair` via `unittest.mock.patch` -- module-level, so it also reaches
`original.py`/`translated.ldpy`'s own `import datetime` (the same singleton
module object via `sys.modules`) without editing either file. This mirrors
harness.py's own `stdout_filter` escape hatch for "a wall-clock duration ...
not the program's meaning", applied here to graph content instead of
stdout.
"""
import datetime as _datetime_module
from unittest.mock import patch

from rdfeval.harness import run_pair


class _FrozenDateTime(_datetime_module.datetime):
    @classmethod
    def utcnow(cls):
        return _datetime_module.datetime(2024, 1, 1, 0, 0, 0)


with patch("datetime.datetime", _FrozenDateTime):
    VERDICT = run_pair(
        __file__,
        entry='demo',
        calls=[((), {})],
    )

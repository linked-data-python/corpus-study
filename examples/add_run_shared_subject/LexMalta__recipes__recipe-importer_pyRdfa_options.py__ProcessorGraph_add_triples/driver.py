"""Validation driver for
LexMalta__recipes__recipe-importer_pyRdfa_options.py__ProcessorGraph_add_triples.

`demo()` (identical on both sides, appended after the extracted region --
see meta.json and original.py's own comment) builds a `ProcessorGraph`
(processor_context.py restores the class this extraction's context window
did not carry -- AGENT_BATCH's "163 regions" case), calls `add_triples`
twice to exercise both branches of `if info_class:` and of
`if context and (...)`, and returns the resulting graph: `run_pair`'s
generic ``entry=``/``calls=`` path already special-cases a returned
``rdflib.Graph`` as isomorphism, which is exactly this region's oracle (it
only ever adds triples).

`add_triples` computes
`Literal(datetime.datetime.utcnow().isoformat(), datatype=ns_xsd["dateTime"])`
for `nsdc:date` -- a live wall-clock value that would make the two sides'
graphs non-isomorphic by construction (two separate calls, microseconds
apart, to the real `utcnow()`), for a reason that has nothing to do with
whether the translation is correct. `datetime.datetime` is frozen for the
duration of `run_pair` via `unittest.mock.patch` -- module-level, so it also
reaches `original.py`/`translated.ldpy`'s own `import datetime` (the same
singleton module object via `sys.modules`) without editing either file.
This mirrors ns_import_project/johnjung.../mepa_edm's own driver.py.
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

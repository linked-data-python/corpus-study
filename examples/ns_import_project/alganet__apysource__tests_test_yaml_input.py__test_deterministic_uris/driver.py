"""Validation driver for alganet__apysource__tests_test_yaml_input.py__test_deterministic_uris.

EXCLUDED (see meta.json): `apysource` is a real, clean PyPI dependency
(0.10.0; only rdflib>=7.0/requests/pyyaml/beautifulsoup4, all satisfiable)
but installing it into ~/.venvs/ldpy was denied by the auto-mode
permission classifier in this session. Faithfully reproducing
`apysource.yaml_input.load_yaml` as a context shim would mean transcribing
its whole import-time dependency chain -- `apysource.schema` (126 lines,
itself importing `apysource.formats`, 921 lines of HTML/Markdown/Wikitext
parsing that additionally needs BeautifulSoup, not installed either) and
`apysource.patterns` (267 lines, importing six `apysource.repos.*`
fetcher classes) -- none of which has anything to do with the
ns_import_project construction this region was sampled for. Writing a
slimmed-down stand-in for ~1400 real lines is exactly what AGENT_BATCH's
shim rule warns against ("n'inventez pas de logique"); it is also
unnecessary, because Python imports the whole chain at module level
regardless of which functions a caller actually uses (`apysource.schema`
does `from apysource.formats import normalize_mime_type` unconditionally),
so a partial shim would not even avoid the blocker.

`_case()` supplies a real writable temp directory (`tempfile.mkdtemp()`,
matching pytest's own `tmp_path` fixture, bypassed here since the region
is called directly) so that a future run WITH `apysource` installed
exercises the real thing unmodified. Today, `_exec_python` on original.py
fails first, at its top-level `from apysource.namespaces import OA,
SCHEMA, SV` (line 14), with `ModuleNotFoundError: No module named
'apysource'` -- confirmed directly (`rdfeval check`, see meta.json's
`validation` -- or the lack of one, since this pair stays draft) -- before
the translated side is ever reached. That IS the excluded verdict, not a
translation defect: the same import fails identically whether or not
`translated.ldpy`'s own `from apysource.namespaces import oa:, schema:,
sv:` is ever exercised.
"""
from pathlib import Path
import tempfile

from rdfeval.harness import run_pair


def _case():
    return ((Path(tempfile.mkdtemp()),), {})


VERDICT = run_pair(
    __file__,
    entry='test_deterministic_uris',
    calls=[_case],
)

"""Validation driver for citiususc__yatter__…__test_yarrrmltc0037.

The region is a YARRRML->RML round-trip test: it parses mapping.ttl, has
yatter translate mapping.yml, and asserts the two graphs are isomorphic.
Both fixture files were copied next to original.py/translated.ldpy (the
region locates them relative to __file__, which the harness sets to each
side's own path).

yatter is not installed in the eval venv; the corpus checkout is put on
sys.path, and its one missing dependency (coloredlogs, used only for log
colouring) is stubbed out.  Both sides run in the same process, so the stub
and the search path are shared identically.
"""
import sys
import types
from pathlib import Path

CORPUS = Path("/home/lefrancois/Documents/recherche/semantic_web_micropython/github"
              "/corpus/repos/citiususc__yatter")

try:
    import yatter  # noqa: F401
except ImportError:
    if "coloredlogs" not in sys.modules:
        _stub = types.ModuleType("coloredlogs")
        _stub.install = lambda *a, **k: None
        sys.modules["coloredlogs"] = _stub
    sys.path.insert(0, str(CORPUS / "src"))

from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry="test_yarrrmltc0037",
                   calls=[lambda: ((), {})])

# Context shim (see meta.json): the real aigora-de/rdf-construct package
# is not published on PyPI, so `from rdf_construct.diff import (...)` (this
# region's own context line, kept verbatim in original.py/translated.ldpy)
# cannot be satisfied by installing anything into the pinned ldpy venv.
# `rdf_construct.diff` (change_types.py, comparator.py, filters.py,
# formatters/) depends on nothing but rdflib and the standard library
# (verified: no other third-party import anywhere under
# src/rdf_construct/diff), so rather than transcribing `compare_graphs`
# and its supporting types by hand -- which would risk silently drifting
# from the real algorithm this region's assertions exercise -- this shim
# adds the pinned commit's own checkout (corpus/repos/aigora-de__rdf-construct,
# fetched for this study) to sys.path and re-exports the names the region
# imports, unchanged. Identical bindings for both representations.
import sys
from pathlib import Path

_REPO_SRC = (Path(__file__).resolve().parents[3]
             / "corpus" / "repos" / "aigora-de__rdf-construct" / "src")
if str(_REPO_SRC) not in sys.path:
    sys.path.insert(0, str(_REPO_SRC))

from rdf_construct.diff import (  # noqa: E402,F401
    compare_graphs,
    filter_diff,
    parse_filter_string,
    ChangeType,
    EntityChange,
    EntityType,
    GraphDiff,
    TripleChange,
    PredicateCategory,
)

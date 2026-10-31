"""Validation driver for bloodbee/jrt teapot_ontology_graph.

The region is a pytest fixture: `@pytest.fixture` wraps the function, so the
entry point cannot be called directly. `demo()` — identical on both sides —
calls the undecorated body through the wrapper's `__wrapped__` and returns
the graph.

Two runs:

  as-written -- run_pair, one call: the graph `demo()` returns, compared by
    isomorphism.  The fixture has no branch and no input, so one call covers
    every triple it writes.

  bindings -- isomorphism does not see prefix bindings, and the region's
    whole point is one: `g.bind("stuff", STUFF)`.  The repository reads it
    back: the `teapot_ontology` fixture (tests/conftest.py:113-118)
    serialises this graph to Turtle, parses the file into a new graph and
    hands it to `Ontology`.  So, per side:
      * every binding of the original's graph must be on the translation's
        (extra ones tolerated: `@graph` adds the block's own, record
        ldpy/027).  A `@prefix st:` for the same IRI, or a `+{ }(g)` call
        suffix that binds nothing, loses `stuff` and fails here;
      * the graph is serialised to Turtle in a temporary directory and
        parsed back, as teapot_ontology does: the parsed graphs must be
        isomorphic, and every prefix the original's file declares must be
        declared by the translation's.
"""
import contextlib
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path

from rdflib import Graph

from rdfeval import harness
from rdfeval.harness import run_pair

ex_dir = Path(__file__).resolve().parent


def _bound(g):
    return {(p, str(n)) for p, n in g.namespaces()}


def _reparsed(g, folder):
    """What teapot_ontology (tests/conftest.py:113-118) does with the graph."""
    path = folder / "ontology.ttl"
    g.serialize(destination=path, format="turtle")
    out = Graph()
    out.parse(path.as_posix(), format="turtle")
    return out


def _bindings():
    left, right = harness.sides_from_env()
    ns_o, _ = harness._exec_artefact(ex_dir / left, "__original__")
    ns_t, _ = harness._exec_artefact(ex_dir / right, "__translated__")
    go, gt = ns_o["demo"](), ns_t["demo"]()
    diffs = []
    missing = _bound(go) - _bound(gt)
    if missing:
        diffs.append(f"graph prefix bindings lost {sorted(missing)}")
    work = Path(tempfile.mkdtemp(prefix="jrt_teapot_"))
    try:
        (work / "o").mkdir()
        (work / "t").mkdir()
        fo, ft = _reparsed(go, work / "o"), _reparsed(gt, work / "t")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    if not harness.graphs_isomorphic(fo, ft):
        diffs.append("re-parsed Turtle files not isomorphic")
    missing = _bound(fo) - _bound(ft)
    if missing:
        diffs.append(f"Turtle file prefixes lost {sorted(missing)}")
    return diffs


def _quiet(**kwargs) -> dict:
    """run_pair's verdict without its stderr line: this driver emits one."""
    with contextlib.redirect_stderr(io.StringIO()):
        return run_pair(**kwargs)


as_written = _quiet(driver_file=__file__, entry='demo', calls=[((), {})])
try:
    extended, extended_error = _bindings(), None
except Exception:
    import traceback
    extended, extended_error = [], traceback.format_exc(limit=8)

verdict = dict(as_written)
verdict["method"] = (f"{as_written.get('method')} (as-written + bindings, "
                     "Turtle round trip)")
verdict["diffs"] = ([f"as-written: {d}" for d in as_written.get("diffs", [])]
                    + [f"bindings: {d}" for d in extended])
errors = [e for e in (as_written.get("error"), extended_error) if e]
verdict["error"] = "\n".join(errors) or None
verdict["equivalent"] = (bool(as_written.get("equivalent"))
                         and not extended and not extended_error)
print("RDFEVAL-VERDICT " + json.dumps(verdict), file=sys.stderr)
VERDICT = verdict

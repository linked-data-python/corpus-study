"""Validation driver for biokb__biokb_wfo__src_biokb_wfo_rdf_turtle.py__TurtleCreator_create_nodes_ttl.

create_nodes_ttl returns only a file path built from self.__ttls_folder --
comparing that return value alone would be a hollow green, since it says
nothing about the graph the region actually built (see context_shim.py:
get_empty_graph stashes the produced graph onto `self.produced_graph`
instead, because create_nodes_ttl calls it bare, not as
self.get_empty_graph()). TurtleCreator.__eq__ compares that graph by
isomorphism, so run_pair's own argument comparison (it compares every call
argument, `self` included, and `self` is args[0] here) becomes the real
oracle.

`self` must be a FRESH object per side (unlike a region where the graph is a
separate, externally-passed argument): create_nodes_ttl mutates a graph it
reaches through `self`, so sharing one `self` between both calls would let
the second call's triples land in the same graph as the first's. The case
factory therefore builds a fresh TurtleCreator per side, from the same rows.

Two runs:

  as-written -- run_pair, one call, four taxon rows exercising the two `if`
    guards independently (each guard's `.add` is its own `+{ }`, never
    merged with the five unconditional ones or with each other):
      * parent_id and ipni both set    -- both guards fire
      * parent_id falsy (0), ipni None -- neither guard fires
      * only parent_id set
      * only ipni set
    Both sides write into one shared directory, so the returned path is the
    same string; the file itself is compared by the second run.

  extended -- each side called directly, in its OWN temporary directory,
    and compared on everything the region decides:
      * the returned path (its file name, and that it is in the side's dir);
      * the graph it built (TurtleCreator.produced_graph), by isomorphism;
      * the prefix bindings of that graph: get_empty_graph binds w, n, r and
        xs (rdf/turtle.py:27-34) and the region serialises the graph to
        nodes.ttl, so every binding of the original must be on the
        translation's (extra ones tolerated, record ldpy/027).  An `@graph
        graph` whose `@prefix xsd:` rebinds XSD away from `xs` fails here;
      * nodes.ttl read back: same triples, and every prefix the original's
        file declares is declared by the translation's;
      * the log records of the module logger (logger.info at entry);
      * stdout, and what it raises (type and message).
    Cases:
      A the as-written rows again;
      B rows of the repository's real shapes: parent_id is a String(50)
        column (db/models.py:183) filled from an Int64 (db/manager.py:179),
        so a digit string, here also "0" (truthy) and "" (falsy); ipni is a
        String(50) or None (manager.py:183), here also "" (falsy, so the
        `if taxon.ipni:` truth test differs from `is not None`); a full_name
        with a quote, a backslash, a newline and non-ASCII letters;
      C no row at all: an empty graph, still serialised.
"""
import contextlib
import io
import json
import logging
import shutil
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

from rdflib import Graph

from context_shim import TurtleCreator

from rdfeval import harness
from rdfeval.harness import run_pair

ex_dir = Path(__file__).resolve().parent


def _rows():
    return [
        SimpleNamespace(id=1, full_name="Taxon One", rank="species",
                         parent_id=10, ipni="12345", role="accepted"),
        SimpleNamespace(id=2, full_name="Taxon Two", rank="genus",
                         parent_id=0, ipni=None, role="synonym"),
        SimpleNamespace(id=3, full_name="Taxon Three", rank="family",
                         parent_id=30, ipni=None, role="accepted"),
        SimpleNamespace(id=4, full_name="Taxon Four", rank="order",
                         parent_id=0, ipni="99999", role="synonym"),
    ]


def _real_rows():
    return [
        SimpleNamespace(id=5, full_name='Rosa "canina" L.\\ é\nx',
                         rank="species", parent_id="12345",
                         ipni="77100000-1", role="accepted"),
        SimpleNamespace(id=6, full_name="Abies", rank="genus",
                         parent_id="0", ipni="", role="synonym"),
        SimpleNamespace(id=7, full_name="Pinaceae", rank="family",
                         parent_id="", ipni=None, role="accepted"),
        SimpleNamespace(id=8, full_name="Pinales", rank="order",
                         parent_id="", ipni="2001-1", role="synonym"),
    ]


CASES = [("A as-written rows", _rows), ("B real shapes", _real_rows),
         ("C no row", list)]

# as-written run: both sides write to the SAME directory, so the returned
# path is the same string on both sides.
_TTLS_DIR = tempfile.mkdtemp()


def factory():
    return ((TurtleCreator(_TTLS_DIR, _rows()),), {})


class _Records(logging.Handler):
    def __init__(self):
        super().__init__(logging.DEBUG)
        self.seen = []

    def emit(self, record):
        self.seen.append((record.levelname, record.getMessage()))


def _call(ns, rows, folder):
    self = TurtleCreator(str(folder), rows)
    logger = ns["logger"]
    records, level = _Records(), logger.level
    logger.addHandler(records)
    logger.setLevel(logging.DEBUG)
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            try:
                result, raised = ns["create_nodes_ttl"](self), None
            except Exception as e:                # noqa: BLE001 - compared
                result, raised = None, (type(e).__name__, str(e))
    finally:
        logger.removeHandler(records)
        logger.setLevel(level)
    ttl = Path(folder) / "nodes.ttl"
    written = Graph().parse(ttl, format="turtle") if ttl.exists() else None
    return {"result": result, "raised": raised, "stdout": out.getvalue(),
            "log": records.seen, "graph": self.produced_graph,
            "file": written, "folder": str(folder)}


def _bound(graph):
    return set() if graph is None else set(graph.namespaces())


def _compare(label, o, t, diffs):
    for key in ("raised", "stdout", "log"):
        if o[key] != t[key]:
            diffs.append(f"{label}: {key} differs ({o[key]!r} vs {t[key]!r})")
    shape = [(r is not None and Path(r).name,
              r is not None and str(Path(r).parent) == f)
             for r, f in ((o["result"], o["folder"]), (t["result"], t["folder"]))]
    if shape[0] != shape[1]:
        diffs.append(f"{label}: returned path differs ({o['result']!r} vs {t['result']!r})")
    for key in ("graph", "file"):
        a, b = o[key], t[key]
        if (a is None) != (b is None) or (
                a is not None and not harness.graphs_isomorphic(a, b)):
            diffs.append(f"{label}: {key} not isomorphic")
        missing = _bound(a) - _bound(b)
        if missing:
            diffs.append(f"{label}: {key} prefix bindings lost "
                         f"{sorted((p, str(n)) for p, n in missing)}")


def _extended():
    left, right = harness.sides_from_env()
    ns_o, _ = harness._exec_artefact(ex_dir / left, "__original__")
    ns_t, _ = harness._exec_artefact(ex_dir / right, "__translated__")
    diffs = []
    for label, rows in CASES:
        work = Path(tempfile.mkdtemp(prefix="biokb_wfo_nodes_"))
        try:
            (work / "o").mkdir()
            (work / "t").mkdir()
            o = _call(ns_o, rows(), work / "o")
            t = _call(ns_t, rows(), work / "t")
        finally:
            shutil.rmtree(work, ignore_errors=True)
        _compare(label, o, t, diffs)
    return diffs


def _quiet(**kwargs) -> dict:
    """run_pair's verdict without its stderr line: this driver emits one."""
    with contextlib.redirect_stderr(io.StringIO()):
        return run_pair(**kwargs)


try:
    as_written = _quiet(driver_file=__file__, entry="create_nodes_ttl",
                        calls=[factory])
finally:
    shutil.rmtree(_TTLS_DIR, ignore_errors=True)
try:
    extended, extended_error = _extended(), None
except Exception:
    import traceback
    extended, extended_error = [], traceback.format_exc(limit=8)

verdict = dict(as_written)
verdict["method"] = (f"{as_written.get('method')} (as-written + extended: "
                     "file, bindings, log, real input shapes)")
verdict["diffs"] = ([f"as-written: {d}" for d in as_written.get("diffs", [])]
                    + [f"extended: {d}" for d in extended])
errors = [e for e in (as_written.get("error"), extended_error) if e]
verdict["error"] = "\n".join(errors) or None
verdict["calls"] = 1 + len(CASES)
verdict["equivalent"] = (bool(as_written.get("equivalent"))
                         and not extended and not extended_error)
print("RDFEVAL-VERDICT " + json.dumps(verdict), file=sys.stderr)
VERDICT = verdict

"""Find pairs whose equivalence check passes without demonstrating anything.

    python scripts/hollow_green.py [--study 403]

A reading region is proved by the equality of the values both versions
produce from the same fixture.  If that value is **empty on both sides** —
no solution, an empty list, ``None`` — the two versions agree on nothing at
all, and the driver goes green without exercising the pattern it was written
for.  The harness cannot see this: it only flags a call that returns
nothing, mutates nothing and prints nothing, and an empty result *is* a
returned value.

Nothing here changes a verdict.  It reports the pairs a reviewer must look
at before an aggregate is computed from them, because a hollow green is
indistinguishable from a real one in the numbers.

**STATUS: a screen that still over-flags — its count is not a measurement.**
Re-running a region outside its driver is not the same as running the driver,
and the difference shows: ``_driver_spec`` swallows whatever the driver raises
and then reports "no entry", so a pair can be listed for a reason that has
nothing to do with its fixture.  Before any number from here is quoted, the
probe has to distinguish "the region found nothing" from "the probe could not
run the region", and be calibrated against pairs whose emptiness is known.
Until then, use the list as a place to look, never as a count.

Exit code is 0 whatever it finds: this is a report, not a gate.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@contextlib.contextmanager
def _in_example(ex_dir: Path):
    """Run inside the example directory, as its validation subprocess does."""
    cwd = os.getcwd()
    os.chdir(ex_dir)
    sys.path.insert(0, str(ex_dir))
    try:
        yield
    finally:
        with contextlib.suppress(ValueError):
            sys.path.remove(str(ex_dir))
        os.chdir(cwd)


def _driver_spec(ex_dir: Path) -> dict | None:
    """The driver's own entry/fixture/calls, by executing it with ``run_pair``
    replaced by a recorder — the file is the source of truth, not its text."""
    driver = ex_dir / "driver.py"
    if not driver.exists():
        return None
    from rdfeval import harness
    captured: dict = {}

    def _record(driver_file, **kw):
        captured.update(kw)
        return {"equivalent": True}

    real, harness.run_pair = harness.run_pair, _record
    try:
        with _in_example(ex_dir), contextlib.redirect_stdout(io.StringIO()):
            exec(compile(driver.read_text(), str(driver), "exec"),
                 {"__name__": "__driver__", "__file__": str(driver)})
    except Exception:
        return None
    finally:
        harness.run_pair = real
    return captured


def _is_empty(value) -> bool:
    """Empty in the sense that matters: the region found nothing."""
    from rdflib import Graph
    if value is None or value is False:
        return True
    if isinstance(value, Graph):
        return len(value) == 0
    if isinstance(value, (list, tuple, set, dict, str)):
        return len(value) == 0
    return False


def observed_value(ex_dir: Path):
    """What the ORIGINAL shows on the driver's own first call case.

    Returns ``(status, evidence)`` where evidence is what a reviewer would
    call the demonstration: the returned value, the triples the call ADDED to
    a graph it was given, and anything it printed. A region that mutates a
    graph returns ``None`` perfectly legitimately — judging it on its return
    value alone would flag it wrongly, so all three are collected.
    """
    from rdfeval.harness import fixture_graph, materialise
    spec = _driver_spec(ex_dir) or {}
    entry = spec.get("entry")
    if not entry:
        return ("no-entry", None)
    calls = spec.get("calls")
    fixture = spec.get("fixture")
    ns: dict = {"__name__": "__probe__",
                "__file__": str(ex_dir / "original.py")}
    with _in_example(ex_dir):
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                exec(compile((ex_dir / "original.py").read_text(),
                             str(ex_dir / "original.py"), "exec"), ns)
            fn = ns.get(entry)
            if not callable(fn):
                return ("no-entry", None)
            if calls:
                case = calls[0]
                args, kw = case() if callable(case) else case
            elif fixture:
                args, kw = (fixture_graph(ex_dir / fixture),), {}
            else:
                args, kw = (), {}
            from rdflib import Graph
            given = [v for v in list(args) + list(kw.values())
                     if isinstance(v, Graph)]
            before = {id(g): len(g) for g in given}
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                returned = materialise(fn(*args, **kw))
            written = sum(len(g) - before[id(g)] for g in given)
            return ("ok", {"returned": returned, "written": written,
                           "printed": len(buf.getvalue().strip())})
        except Exception as e:                       # noqa: BLE001
            return ("error: %s" % type(e).__name__, None)


# ---------------------------------------------------------------------------
# A second screen, and this one IS reliable: it is static.
# ---------------------------------------------------------------------------

def shared_graph_objects(study) -> list:
    """Shims that build a graph at module level — a possible vacuous check.

    Both sides of a pair import the shim, and Python caches modules: a
    ``Graph()`` created at a shim's module level is therefore **the same
    object** for the original and the translation. If that graph is the one
    the driver compares, the isomorphism check compares it to itself and
    passes even when the translation is broken. One such pair was found by
    hand in the 2026-08-29 wave (a shim exporting the output graph).

    Sharing is only dangerous for an OUTPUT. A shared graph that the region
    merely READS is the fixture pattern and is correct — so this returns
    candidates to inspect, not defects. Unlike the emptiness probe above,
    it reads source and runs nothing, so what it reports is exactly what is
    there.
    """
    import ast
    from rdfeval.validate import iter_examples
    out = []
    for ex_dir, meta in iter_examples(study):
        if meta.get("translation_status") != "final":
            continue
        for shim in sorted(Path(ex_dir).glob("*.py")):
            if shim.name in ("original.py", "driver.py"):
                continue
            try:
                tree = ast.parse(shim.read_text())
            except (SyntaxError, OSError):
                continue
            for node in tree.body:          # module level only
                if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                    continue
                call = node.value
                if not isinstance(call, ast.Call):
                    continue
                name = getattr(call.func, "id",
                               getattr(call.func, "attr", ""))
                if name in ("Graph", "Dataset", "ConjunctiveGraph"):
                    out.append((meta.get("stratum", "?"), meta["region_id"],
                                shim.name))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", default="403", choices=("401", "403"))
    args = ap.parse_args()
    from rdfeval.study import get as get_study
    from rdfeval.validate import iter_examples

    study = get_study(args.study)
    hollow, probed, skipped = [], 0, 0
    for ex_dir, meta in iter_examples(study):
        if meta.get("translation_status") != "final":
            continue
        if (meta.get("validation") or {}).get("status") != "equivalent":
            continue
        status, value = observed_value(Path(ex_dir))
        if status != "ok":
            skipped += 1
            continue
        probed += 1
        # hollow only if NOTHING was shown: no value, no triple written into
        # a graph the call was given, nothing printed
        if (_is_empty(value["returned"]) and not value["written"]
                and not value["printed"]):
            hollow.append((meta.get("stratum", "?"), meta["region_id"],
                           type(value["returned"]).__name__))

    print("hollow-green probe over study %s" % study.name)
    print("  %d equivalent pairs probed, %d not probeable in-process"
          % (probed, skipped))
    print("  %d produce an EMPTY result on the original side" % len(hollow))
    for stratum, rid, kind in sorted(hollow):
        print("    %-24s %s  (%s)" % (stratum, rid[:64], kind))
    if hollow:
        print("\nThese pass without exercising anything: their fixture holds "
              "no solution of the\npattern they translate. Give them a "
              "fixture that does, or record why none exists.")

    shared = shared_graph_objects(study)
    print("\nstatic screen: %d pair(s) whose shim builds a graph at module "
          "level" % len(shared))
    for stratum, rid, shim in sorted(shared):
        print("    %-24s %s  (%s)" % (stratum, rid[:60], shim))
    if shared:
        print("\nBoth sides import the shim and Python caches modules, so that "
              "graph is ONE object.\nHarmless when the region only READS it "
              "(that is the fixture pattern); vacuous when it\nis the graph "
              "the driver compares. Look at each one.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

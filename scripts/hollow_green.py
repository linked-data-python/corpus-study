"""Find pairs whose equivalence check passes without demonstrating anything.

    python scripts/hollow_green.py

A reading region is proved by the equality of the values both versions
produce from the same fixture.  If that value is **empty on both sides** —
no solution, an empty list, ``None`` — the two versions agree on nothing at
all, and the driver goes green without exercising the pattern it was written
for.  The harness's ``observed`` check cannot see this: an empty result *is*
a returned value.

The screen is the harness itself.  ``run_pair`` records, for every call of
the driver, whether the ORIGINAL showed anything — a non-empty value, a
raise, a change to what it was given (graphs by digest, a stub ``self`` by
its attributes), or output — and puts ``hollow: true`` in the verdict when
no call did.  This script runs each driver exactly as validation does
(:func:`rdfeval.check.check`) and lists those verdicts, so "the region found
nothing" can no longer be confused with "the probe could not run the
region": a driver that does not run is reported as such.  A hand-written
driver that does not go through ``run_pair`` gives no ``hollow`` key and is
counted apart.

Nothing here changes a verdict.  It reports the pairs a reviewer must look
at before an aggregate is computed from them, because a hollow green is
indistinguishable from a real one in the numbers.

Exit code is 0 whatever it finds: this is a report, not a gate.
"""

from __future__ import annotations

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def screen(ex_dirs) -> list:
    """``(ex_dir, status)`` per region: ``hollow``, ``shown``, ``unscreened``
    (no ``run_pair`` verdict) or ``failed`` (the check itself fails)."""
    from rdfeval.check import check

    def one(ex_dir):
        r = check(Path(ex_dir))
        verdict = r.get("verdict") or {}
        if not r.get("ok"):
            return ex_dir, "failed"
        if "hollow" not in verdict:
            return ex_dir, "unscreened"
        return ex_dir, "hollow" if verdict["hollow"] else "shown"

    with ThreadPoolExecutor(8) as pool:
        return list(pool.map(one, ex_dirs))


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
            if shim.name in ("original.py", "driver.py", "optimized.py"):
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
    ap.add_argument("--study", default=None, help="accepted and ignored")
    args = ap.parse_args()
    from collections import Counter
    from rdfeval.study import get as get_study
    from rdfeval.validate import iter_examples

    study = get_study(args.study)
    todo = {ex_dir: meta for ex_dir, meta in iter_examples(study)
            if meta.get("translation_status") == "final"
            and (meta.get("validation") or {}).get("status") == "equivalent"}
    results = screen(list(todo))
    counts = Counter(status for _, status in results)
    print("hollow-green screen over study %s: %d equivalent pairs"
          % (study.name, len(results)))
    print("  %d show something on the original side, %d show nothing, "
          "%d not screened (driver bypasses run_pair), %d failing the check"
          % (counts["shown"], counts["hollow"], counts["unscreened"],
             counts["failed"]))
    for status in ("hollow", "failed", "unscreened"):
        rows = sorted((todo[ex].get("stratum", "?"), todo[ex]["region_id"])
                      for ex, st in results if st == status)
        if rows:
            print("\n%s:" % status)
            for stratum, rid in rows:
                print("    %-24s %s" % (stratum, rid[:64]))
    if counts["hollow"]:
        print("\nThe hollow ones pass without exercising anything: no call "
              "of their driver gets\na value, a raise, a change or an "
              "output out of the original. Give them a\ncase that does, or "
              "record why none exists.")

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

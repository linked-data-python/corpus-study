"""Stratified, seeded draw of code regions by *type of use* (corpus/403).

The evaluation of design record ``corpus/401`` sampled files by RDF density
and asked how much of the notation's *construction* half the corpus absorbs.
This stage answers the other question: for each **kind of use** of rdflib
found by the surface analysis (record ``corpus/402``), is the construction
the language proposes for it useful, where, and how often?

The draw therefore has strata, not bands.  Its population is the site index
``results/raw/sites.jsonl`` written by :mod:`rdfeval.surface` — one record
per located occurrence of a stratum shape — and its unit is the **region**
enclosing a site, extracted here.

Determinism
    Sites are sorted by a stable key (repository, path, line, kind) before
    ``random.Random(seed)`` draws, so the same corpus and configuration
    always yield the same sample.  Like :func:`rdfeval.sample.draw_wave`,
    enlarging a quota tops the sample up instead of re-drawing it.

Overlap
    The strata overlap by design (a run of adds inside a loop is a site of
    three of them), so one region may be drawn for several strata.  It is
    translated **once** and credited to each: the draw carries a region's
    full list of strata, and the per-construction counters read that list.

Outputs::

    results/raw/strata.json       the drawn regions, with source and context
    results/summary/strata.csv    one row per stratum: population and draw
    examples/<stratum>/<id>/   one directory per region, with its draft

The example tree is separate from the 401 study's ``examples/``: the two
answer different questions with different oracles, and their aggregates must
never mix under one number.
"""

from __future__ import annotations

import ast
import csv
import json
import random
import textwrap
from collections import defaultdict

from .acquire import repo_dir
from .config import EXAMPLES_DIR, RESULTS_RAW, RESULTS_SUMMARY, provenance
from .regions import _functions, _names_read, _span
from .surface import SITES_RAW, STRATA

STRATA_PATH = RESULTS_RAW / "strata.json"
STRATA_CSV = RESULTS_SUMMARY / "strata.csv"


def load_sites() -> tuple[dict, list[dict]]:
    """(header, sites) from the site index; raises if surface has not run."""
    if not SITES_RAW.exists():
        raise SystemExit("no site index; run `rdfeval surface` first")
    rows = [json.loads(line) for line in
            SITES_RAW.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        raise SystemExit(f"{SITES_RAW} is empty")
    return rows[0], rows[1:]


# --- the region enclosing a site --------------------------------------------

def region_for_site(source: str, line: int, rcfg: dict) -> dict | None:
    """The smallest sensible region of ``source`` that contains ``line``.

    Preference order, and why:

    1. the **innermost enclosing function** that fits in ``max_region_loc`` —
       a function is the unit a reader and a translator both work with;
    2. the whole **file**, when it fits — a site at module level needs the
       module's own preamble to mean anything;
    3. the **largest enclosing statement** that fits — inside a 600-line
       function, the `for` loop around the site is the honest unit;
    4. nothing: the site is inside a single statement longer than the cap,
       and is reported as undrawable rather than truncated.

    A **declaration site** — an import of project namespaces, a
    ``NS = Namespace(...)`` — is a special case: on its own it carries no RDF
    operation, and translating one line demonstrates nothing.  When the
    region chosen for such a site holds fewer than ``min_rdf_ops``
    operations, the region becomes the smallest function that *uses* the
    names the site binds, the declaration itself coming along as context.
    """
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError, MemoryError, RecursionError):
        return None
    lines = source.splitlines()
    cap = rcfg["max_region_loc"]
    chosen = _region_for_line(tree, lines, line, cap)
    if chosen is not None and chosen["rdf_ops"] >= rcfg["min_rdf_ops"]:
        return chosen
    user = _region_using(tree, lines, line, rcfg)
    return user if user is not None else chosen


def _bound_names(tree: ast.AST, line: int) -> set[str]:
    """Names bound by the statement at ``line`` (an import, an assignment)."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.stmt) or node.lineno != line:
            continue
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return {(a.asname or a.name).split(".")[0] for a in node.names}
        targets = node.targets if isinstance(node, ast.Assign) else (
            [node.target] if isinstance(node, ast.AnnAssign) else [])
        return {t.id for t in targets if isinstance(t, ast.Name)}
    return set()


def _region_using(tree, lines, line: int, rcfg: dict) -> dict | None:
    """Smallest function that reads a name bound at ``line`` and does RDF work."""
    names = _bound_names(tree, line)
    if not names:
        return None
    best = None
    for qual, node in _functions(tree):
        lo, hi = _span(node)
        if hi - lo + 1 > rcfg["max_region_loc"] or not (_names_read(node) & names):
            continue
        candidate = _region(lines, tree, lo, hi, qual, node, "function")
        if candidate["rdf_ops"] < rcfg["min_rdf_ops"]:
            continue
        if best is None or hi - lo < best[1] - best[0]:
            best = (lo, hi, qual, node)
    if best is None:
        return None
    lo, hi, qual, node = best
    region = _region(lines, tree, lo, hi, qual, node, "function")
    region["declaration_site_line"] = line
    return region


def _region_ops(region: dict) -> list:
    """RDF operations a region performs, read the way a reader would.

    A region lifted out of a function has no imports of its own, and the
    analyser's name resolution is flow-insensitive: without the module
    bindings it comes back with `g` unknown and zero operations.  The
    region's context lines are exactly those bindings, so they are the
    preamble.
    """
    from .analyze import analyze_source
    try:
        fa = analyze_source(textwrap.dedent(region["source"]),
                            preamble="\n".join(region["context"]) or None)
    except (SyntaxError, ValueError, RecursionError):
        return []
    return fa.ops


def _region_for_line(tree, lines, line: int, cap: int) -> dict | None:
    """Steps 1-3 of :func:`region_for_site`: the unit, before RDF weighing."""
    enclosing = []
    for qual, node in _functions(tree):
        lo, hi = _span(node)
        if lo <= line <= hi:
            enclosing.append((hi - lo, lo, hi, qual, node))
    enclosing.sort()
    for size, lo, hi, qual, node in enclosing:
        if size + 1 <= cap:
            return _region(lines, tree, lo, hi, qual, node, "function")

    if len(lines) <= cap:
        return _region(lines, tree, 1, len(lines), "<module>", tree, "file")

    best = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.stmt):
            continue
        lo, hi = _span(node)
        if lo <= line <= hi and hi - lo + 1 <= cap:
            if best is None or hi - lo > best[1] - best[0]:
                best = (lo, hi, node)
    if best is None:
        return None
    lo, hi, node = best
    qual = enclosing[0][3] if enclosing else "<module>"
    return _region(lines, tree, lo, hi, qual, node, "statement")


def _context_for(tree, lines, node, lo: int, kind: str) -> list[str]:
    """Module-level statements the region needs, resolved to a fixpoint.

    Two corrections over :func:`rdfeval.regions._module_context`, both found
    by a translator agent on a real region:

    * a **statement** region sees only what precedes it.  A later
      ``bad = [LATER.z]`` was being handed to it as context, which *rebinds*
      a name the region reads — the region no longer starts from the state
      the file gives it.  (A **function** region keeps later bindings: a
      module-level name defined after a ``def`` is available when it is
      called, which is Python's rule, not an accident.)
    * the context lines have needs of their own.  ``EX = Namespace(...)``
      requires ``from rdflib import Namespace``, and that import was missing
      whenever the region did not name ``Namespace`` itself.  Names are
      therefore collected to a fixpoint.
    """
    if isinstance(node, ast.Module):
        return []
    body = [st for st in tree.body
            if kind != "statement" or getattr(st, "lineno", 0) < lo]
    needed = _names_read(node)
    chosen: list[ast.stmt] = []
    seen: set[int] = set()
    for _ in range(8):                       # fixpoint, bounded
        picked = _binding_statements(body, needed)
        new = [st for st in picked if id(st) not in seen]
        if not new:
            break
        for st in new:
            seen.add(id(st))
        chosen.extend(new)
        for st in new:
            needed |= _names_read(st)
    chosen.sort(key=lambda st: st.lineno)
    return ["\n".join(lines[st.lineno - 1:st.end_lineno]) for st in chosen]


def _binding_statements(body, needed: set[str]) -> list[ast.stmt]:
    out = []
    for stmt in body:
        binds: set[str] = set()
        if isinstance(stmt, (ast.Import, ast.ImportFrom)):
            for alias in stmt.names:
                binds.add((alias.asname or alias.name).split(".")[0])
        elif isinstance(stmt, ast.Assign):
            for t in stmt.targets:
                if isinstance(t, ast.Name):
                    binds.add(t.id)
        elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            binds.add(stmt.target.id)
        if binds & needed:
            out.append(stmt)
    return out


def _region(lines, tree, lo, hi, qual, node, kind) -> dict:
    region = {
        "kind": kind,
        "qualname": qual,
        "lineno": lo,
        "end_lineno": hi,
        "loc": hi - lo + 1,
        "source": "\n".join(lines[lo - 1:hi]),
        "context": _context_for(tree, lines, node, lo, kind),
    }
    # Operations the region performs *as extracted*.  Zero does not mean the
    # site was imaginary: the surface pass saw the whole file, where a graph
    # may be bound by an attribute or a parameter the context lines cannot
    # carry.  It means the translator must restore that binding, so it is
    # recorded rather than silently dropped.
    ops = _region_ops(region)
    region["rdf_ops"] = len(ops)
    region["categories"] = _categories(ops)
    return region


def _categories(ops) -> dict:
    counts: dict[str, int] = {}
    for op in ops:
        counts[op.category] = counts.get(op.category, 0) + 1
    return dict(sorted(counts.items()))


def _region_id(repository: str, path: str, qualname: str, lineno: int) -> str:
    base = (f"{repository.replace('/', '__')}"
            f"__{path.replace('/', '_')}"
            f"__{qualname.replace('.', '_')}")
    return base if qualname != "<module>" else f"{base}_{lineno}"


# --- the draw ----------------------------------------------------------------

def draw(sites: list[dict], scfg: dict, rcfg: dict, eligible: set[str],
         source_of, previous: dict[str, dict] | None = None) -> dict:
    """Draw up to ``target`` regions per stratum, capped per repository.

    ``source_of(repository, path) -> str | None`` reads a corpus file;
    injecting it keeps this function testable without a checkout.

    ``previous`` is the ``regions`` map of an earlier draw: those regions are
    RETAINED — raising a target tops the sample up, it never re-draws it, so
    translations already reviewed stay valid (the rule of
    :func:`rdfeval.sample.draw_wave`).
    """
    previous = previous or {}
    rng = random.Random(scfg["seed"])
    by_kind: dict[str, list[dict]] = defaultdict(list)
    for site in sites:
        if site["repository"] in eligible:
            by_kind[site["kind"]].append(site)

    regions: dict[str, dict] = {rid: dict(r) for rid, r in previous.items()}
    per_stratum: dict[str, dict] = {}
    for kind in STRATA:
        pool = sorted(by_kind.get(kind, []),
                      key=lambda s: (s["repository"], s["path"], s["line"]))
        target = scfg["target_per_stratum"]
        cap = scfg["max_per_repo_per_stratum"]
        order = list(range(len(pool)))
        rng.shuffle(order)
        # Regions this stratum already holds, from an earlier wave.  They
        # count towards both the target and the per-repository cap.
        chosen: list[str] = [rid for rid, r in regions.items()
                             if kind in r.get("strata", [])]
        per_repo: dict[str, int] = defaultdict(int)
        for rid in chosen:
            per_repo[regions[rid]["repository"]] += 1
        undrawable = 0
        for i in order:
            if len(chosen) >= target:
                break
            site = pool[i]
            if per_repo[site["repository"]] >= cap:
                continue
            source = source_of(site["repository"], site["path"])
            if source is None:
                undrawable += 1
                continue
            region = region_for_site(source, site["line"], rcfg)
            if region is None:
                undrawable += 1
                continue
            rid = _region_id(site["repository"], site["path"],
                             region["qualname"], region["lineno"])
            if rid in chosen:
                continue
            record = regions.setdefault(rid, {
                **region,
                "region_id": rid,
                "repository": site["repository"],
                "path": site["path"],
                "commit": site.get("commit"),
                "strata": [],
                "sites": [],
            })
            if kind not in record["strata"]:
                record["strata"].append(kind)
            record["sites"].append({"kind": kind, "line": site["line"],
                                    "end_line": site["end_line"]})
            chosen.append(rid)
            per_repo[site["repository"]] += 1
        per_stratum[kind] = {
            "description": STRATA[kind],
            "population_sites": len(pool),
            "population_repositories": len({s["repository"] for s in pool}),
            "drawn_regions": len(chosen),
            "target": target,
            "undrawable_sites": undrawable,
            "repositories_drawn": len(per_repo),
        }
    return {"strata": per_stratum, "regions": regions}


def _source_reader(config: dict):
    cache: dict[tuple[str, str], str | None] = {}

    def read(repository: str, path: str) -> str | None:
        key = (repository, path)
        if key not in cache:
            full = repo_dir(config, repository) / path
            try:
                cache[key] = full.read_text(encoding="utf-8", errors="replace")
            except OSError:
                cache[key] = None
        return cache[key]

    return read


def _previous_draw() -> dict[str, dict]:
    """The regions of an earlier draw, kept so a wave tops up (never re-draws)."""
    if not STRATA_PATH.exists():
        return {}
    return json.loads(STRATA_PATH.read_text()).get("regions", {})


def run(config: dict) -> None:
    from .select import load_manifest

    scfg = config["strata"]
    rcfg = config["regions"]
    _header, sites = load_sites()
    eligible = {m["full_name"] for m in load_manifest()
                if m.get("snippet_ok") and not m.get("pruned")}
    result = draw(sites, scfg, rcfg, eligible, _source_reader(config),
                  _previous_draw())

    out = {
        "provenance": provenance(config),
        "seed": scfg["seed"],
        "target_per_stratum": scfg["target_per_stratum"],
        "max_per_repo_per_stratum": scfg["max_per_repo_per_stratum"],
        "eligible_repositories": len(eligible),
        "strata": result["strata"],
        "regions": result["regions"],
    }
    STRATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    STRATA_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False),
                           encoding="utf-8")
    STRATA_CSV.parent.mkdir(parents=True, exist_ok=True)
    with STRATA_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["stratum", "construction", "population_sites",
                    "population_repositories", "target", "drawn_regions",
                    "repositories_drawn", "undrawable_sites"])
        for kind, st in result["strata"].items():
            w.writerow([kind, st["description"], st["population_sites"],
                        st["population_repositories"], st["target"],
                        st["drawn_regions"], st["repositories_drawn"],
                        st["undrawable_sites"]])
    _report(out)
    if config["strata"].get("materialise", True):
        print("translate:", materialise_all(config))


def _report(out: dict) -> None:
    regions = out["regions"]
    print(f"strata: {len(regions)} distinct regions drawn "
          f"(seed {out['seed']}, target {out['target_per_stratum']}/stratum)")
    for kind, st in out["strata"].items():
        short = "" if st["drawn_regions"] >= st["target"] else \
            f"  ! only {st['drawn_regions']}/{st['target']}"
        print(f"  {kind:24s} {st['drawn_regions']:4d} regions "
              f"of {st['population_sites']:6d} sites "
              f"in {st['population_repositories']:4d} repos{short}")
    shared = sum(1 for r in regions.values() if len(r["strata"]) > 1)
    kinds = defaultdict(int)
    for r in regions.values():
        kinds[r["kind"]] += 1
    no_ops = sum(1 for r in regions.values() if not r.get("rdf_ops"))
    print(f"  {shared} regions belong to more than one stratum; "
          f"units: {dict(kinds)}")
    print(f"  {no_ops} regions carry no RDF operation once extracted "
          f"(a graph bound outside the region: the translator restores it)")


def materialise_all(config: dict) -> dict[str, int]:
    """Write one example directory per drawn region, under ``examples/``.

    A region is filed under its **first** stratum — the draw order — and its
    ``meta.json`` carries the full list, so a region serving three strata is
    written once and counted three times.
    """
    from .translate import materialise

    draw_result = load_draw()
    counts: dict[str, int] = {}
    for region in draw_result["regions"].values():
        reg = dict(region)
        reg["stratum"] = reg["strata"][0]
        status = materialise(reg, config, root=EXAMPLES_DIR,
                             group="stratum")
        counts[status] = counts.get(status, 0) + 1
        review = (EXAMPLES_DIR / reg["stratum"] / reg["region_id"]
                  / "review.json")
        if not review.exists():
            # Incremental human review (fiche 403): the aggregates are always
            # recomputed on the approved subset, never on the drafts.
            review.write_text(json.dumps({
                "region_id": reg["region_id"],
                "review_status": "unreviewed",
                "reviewer": None,
                "reviewed_at": None,
                "comment": None,
            }, indent=2, ensure_ascii=False), encoding="utf-8")
    return counts


def load_draw() -> dict:
    if not STRATA_PATH.exists():
        raise SystemExit("no stratified draw; run `rdfeval strata` first")
    return json.loads(STRATA_PATH.read_text())

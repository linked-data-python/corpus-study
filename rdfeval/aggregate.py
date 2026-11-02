"""Aggregate statistics, tables and figures over the measured pairs.

Reads results/raw/pairs.jsonl (+ validation), computes distributions —
never just means — and writes:

    results/summary/aggregate.json     all aggregate numbers
    results/summary/aggregate_bands.csv  per-band table
    results/summary/fig_reduction.pdf/.png    reduction distributions
    results/summary/fig_density_benefit.pdf/.png  density vs benefit
    results/summary/fig_correspondence.pdf/.png   per-triple correspondence

Only pairs whose semantic equivalence is established ("equivalent") enter
the headline aggregates; unresolved/not-equivalent pairs are reported
separately so nothing is silently dropped.
"""

from __future__ import annotations

import json
import statistics as st

from .compare import load_pairs
from .config import RESULTS_RAW, RESULTS_SUMMARY, provenance
from .stats import paired_report
from .study import Study, STUDY

METRICS = ("code_loc", "tokens", "chars", "syntax_nodes")


def _dist(values: list[float]) -> dict | None:
    vs = [v for v in values if v is not None]
    if not vs:
        return None
    vs.sort()
    q = st.quantiles(vs, n=4) if len(vs) >= 2 else [vs[0]] * 3
    return {
        "n": len(vs),
        "mean": round(st.mean(vs), 4),
        "median": round(st.median(vs), 4),
        "q1": round(q[0], 4), "q3": round(q[2], 4),
        "min": round(vs[0], 4), "max": round(vs[-1], 4),
    }


def _reduction(row: dict, metric: str) -> float | None:
    a = row["python"].get(metric)
    b = row["ldpy"].get(metric)
    if not a:
        return None
    return round(100.0 * (a - b) / a, 3)


def run(config: dict, study: Study = STUDY, force: bool = False) -> None:
    """Aggregate the measured pairs.

    ``force`` aggregates over every pair with a finished translation instead
    of the approved subset. The numbers are then PROVISIONAL: an agent's
    translation is a hypothesis until a human has read it, and the gate exists
    so that no published figure quietly rests on one. Every artefact says
    which basis it used — ``pairs_reviewed_basis`` in the JSON, a banner on
    the console — so a forced run can never be mistaken for a reviewed one.
    """
    pairs = load_pairs(study)
    reprise = _reprise_selection(study) if study.incremental_review else None
    outside = []
    if reprise is not None:
        # the sample is the resumed selection (record corpus/404): a final
        # pair left out of it — its region lost every stratum it was drawn
        # for when the analyser was corrected — is measured, not published
        selected = {r for _, sel in reprise.values() for r in sel}
        outside = [p["region_id"] for p in pairs
                   if p["region_id"] not in selected]
        pairs = [p for p in pairs if p["region_id"] in selected]
    translated = len(pairs)
    approved = [p for p in pairs if p.get("review_status") == "approved"]
    if study.incremental_review and not force:
        # Record corpus/403: the published aggregates are recomputed on demand over
        # the APPROVED subset only, and always say over how many.  A draft an
        # agent produced is a hypothesis, not a measurement.
        print(f"aggregate: {len(approved)} approved of {translated} translated")
        pairs = approved
    elif force:
        print(f"aggregate: --force — {translated} translated, "
              f"{len(approved)} of them approved; "
              f"the numbers below are PROVISIONAL")
    ok = [p for p in pairs if p["validation_status"] == "equivalent"]
    other = [p for p in pairs if p["validation_status"] != "equivalent"]

    agg: dict = {"provenance": provenance(config),
                 "study": study.name,
                 "pairs_translated": translated,
                 "pairs_reviewed_basis": (
                     "all final (--force, PROVISIONAL)" if force
                     else "approved" if study.incremental_review
                     else "all final"),
                 "pairs_approved": len(approved),
                 "pairs_outside_selection": sorted(outside),
                 "pairs_total": len(pairs),
                 "pairs_equivalent": len(ok),
                 "pairs_other": [
                     {"region_id": p["region_id"],
                      "status": p["validation_status"]} for p in other],
                 "by_metric": {}, "by_band": {}, "by_repository": {},
                 "correspondence": {}, "classification_counts": {}}

    for p in pairs:
        c = p.get("classification") or "unclassified"
        agg["classification_counts"][c] = agg["classification_counts"].get(c, 0) + 1

    for metric in METRICS:
        agg["by_metric"][metric] = {
            "reduction_pct": _dist([_reduction(p, metric) for p in ok]),
            "ratio": _dist([p["ratios"].get(metric) for p in ok]),
            # paired, distribution-free comparison of the raw measurements
            "paired": paired_report([p["python"].get(metric) for p in ok],
                                    [p["ldpy"].get(metric) for p in ok]),
        }

    # --- where the RDF lives in the original source -------------------------
    # The headline surface numbers mix three very different situations; the
    # subgroup breakdown is the honest way to read them (see the README).
    for sg in sorted({p.get("subgroup") for p in ok if p.get("subgroup")}):
        sub = [p for p in ok if p.get("subgroup") == sg]
        agg["by_subgroup"] = agg.get("by_subgroup", {})
        agg["by_subgroup"][sg] = {
            "n": len(sub),
            "byte_identical": sum(1 for p in sub if p["ldpy"]["islands"] == 0),
            **{m: _dist([_reduction(p, m) for p in sub]) for m in METRICS},
            "correspondence": {
                m: {"python": _dist([p["python"].get(m) for p in sub]),
                    "ldpy": _dist([p["ldpy"].get(m) for p in sub]),
                    "paired": paired_report([p["python"].get(m) for p in sub],
                                            [p["ldpy"].get(m) for p in sub])}
                for m in ("corr_scaffolding_tokens_per_triple",
                          "corr_nesting_per_term",
                          "corr_constructors_per_triple")},
        }

    bands = sorted({p[study.group] for p in ok})
    for band in bands:
        sub = [p for p in ok if p[study.group] == band]
        agg["by_band"][band] = {
            "n": len(sub),
            **{m: _dist([_reduction(p, m) for p in sub]) for m in METRICS},
        }
    for repo in sorted({p["repository"] for p in ok}):
        sub = [p for p in ok if p["repository"] == repo]
        agg["by_repository"][repo] = {
            "n": len(sub),
            "tokens_reduction": _dist([_reduction(p, "tokens") for p in sub]),
        }

    corr_metrics = ("corr_scaffolding_tokens_per_triple",
                    "corr_nesting_per_term", "corr_constructors_per_triple")
    agg["correspondence"] = {
        m: {"python": _dist([p["python"].get(m) for p in ok]),
            "ldpy": _dist([p["ldpy"].get(m) for p in ok]),
            "paired": paired_report([p["python"].get(m) for p in ok],
                                    [p["ldpy"].get(m) for p in ok])}
        for m in corr_metrics
    }
    agg["correspondence"]["python_staging_assignments_total"] = sum(
        p["python"].get("corr_staging_assignments") or 0 for p in ok)

    # density vs benefit (the §4 research question)
    agg["density_vs_benefit"] = [
        {"region_id": p["region_id"], study.group: p[study.group],
         "rdf_ops": p["python"]["rdf_ops"],
         "rdf_op_share": round(p["python"]["rdf_ops"]
                               / max(p["python"]["syntax_nodes"], 1), 5),
         "tokens_reduction_pct": _reduction(p, "tokens")}
        for p in ok]

    if study.incremental_review:
        agg["by_stratum"] = _by_stratum(ok, reprise, _outcomes(study, force))
        agg["optimized"] = _optimized(ok)
        agg["by_construction"] = _by_construction(ok)
        agg["unattested_constructions"] = _unattested(ok)
        agg["by_oracle"] = {
            o: len([p for p in ok if p.get("oracle") == o])
            for o in sorted({p.get("oracle") for p in ok if p.get("oracle")})}

    RESULTS_SUMMARY.mkdir(parents=True, exist_ok=True)
    with open(study.path(RESULTS_SUMMARY / "aggregate.json"), "w") as f:
        json.dump(agg, f, indent=2, ensure_ascii=False)

    _band_csv(agg, study)
    try:
        _figures(ok, agg, study)
    except ImportError:
        print("  (matplotlib unavailable: figures skipped)")
    if not ok:
        print("aggregate: no equivalent pair yet — nothing to aggregate")
        return
    print(f"aggregate: {len(ok)} equivalent pairs aggregated; "
          f"medians tokens {agg['by_metric']['tokens']['reduction_pct']}")


EXPRESSIBLE = ("directly-expressible", "minor-restructuring")


def _outcomes(study: Study = STUDY, force: bool = False) -> list[dict]:
    """Every proved outcome of a region, measured or not.

    A ``not-expressible`` region is a result, not a pair: ``compare`` does
    not measure it, so the measured pairs alone would make every stratum
    look expressible.  The rate of expressibility is read here — over the
    finals whose equivalence is proved, and the ``not-expressible`` ones —
    under the same review gate as the pairs."""
    from .compare import _review_status
    from .validate import iter_examples
    out = []
    for ex_dir, meta in iter_examples(study):
        if meta.get("translation_status") != "final" or meta.get("disabled"):
            continue
        cls = meta.get("classification")
        if cls == "excluded":
            continue
        proved = (meta.get("validation") or {}).get("status") == "equivalent"
        if cls != "not-expressible" and not proved:
            continue
        if study.incremental_review and not force \
                and _review_status(ex_dir) != "approved":
            continue
        out.append({"region_id": meta["region_id"],
                    "strata": meta.get("strata", []),
                    "classification": cls})
    return out


def _by_stratum(ok: list[dict], reprise: dict | None = None,
                outcomes: list[dict] | None = None) -> dict:
    """Coverage and benefit per stratum of use (fiche 403).

    A pair drawn for several strata counts in each: the question is whether
    the construction proposed for *that* use pays, and one region can answer
    for several.

    **String-embedded pairs are reported apart, never pooled.**  RDF written
    as text inside a Python string is ONE token to Python's tokenizer; making
    it visible as an island multiplies the token count for a reason that has
    nothing to do with notation quality (see ``compare.string_embedded_rdf``).
    Whole strata are string-embedded by nature — every SPARQL query is — so
    pooling them would publish, for `sparql_literal`, a token "reduction" of
    -186 % that means only "the query text is now counted".
    """
    out: dict = {}
    for stratum in sorted({s for p in ok for s in p.get("strata", [])}):
        sub = [p for p in ok if stratum in p.get("strata", [])]
        if reprise is not None:
            # the resumed selection (record corpus/404): a pair that lost
            # the stratum with the analyser correction no longer counts in it
            selected = reprise.get(stratum, (0.0, {}))[1]
            sub = [p for p in sub if p["region_id"] in selected]
            if not sub:
                continue
        classes: dict[str, int] = {}
        for p in sub:
            classes[p.get("classification") or "unclassified"] = \
                classes.get(p.get("classification") or "unclassified", 0) + 1
        comparable = [p for p in sub if p.get("subgroup") != "string-embedded"]
        embedded = [p for p in sub if p.get("subgroup") == "string-embedded"]
        out[stratum] = {
            "n": len(sub),
            "n_surface_comparable": len(comparable),
            "n_string_embedded": len(embedded),
            "classification": dict(sorted(classes.items())),
            "expressible": sum(1 for p in sub
                               if p.get("classification") in EXPRESSIBLE),
            "by_subgroup": {sg: len([p for p in sub if p.get("subgroup") == sg])
                            for sg in sorted({p.get("subgroup") for p in sub})},
            **{m: _dist([_reduction(p, m) for p in comparable])
               for m in METRICS},
            "string_embedded": {
                m: _dist([_reduction(p, m) for p in embedded]) for m in METRICS
            } if embedded else None,
        }
        if outcomes is not None:
            decided = [o for o in outcomes if stratum in o["strata"]
                       and (reprise is None or o["region_id"] in selected)]
            out[stratum]["coverage"] = {
                "finals": len(decided),
                "expressible": sum(1 for o in decided
                                   if o["classification"] in EXPRESSIBLE),
                "not_expressible": sum(1 for o in decided if
                                       o["classification"] == "not-expressible"),
            }
        if reprise is not None:
            out[stratum]["weighted"] = _weighted(
                sub, comparable, *reprise.get(stratum, (0.0, {})),
                decided if outcomes is not None else sub)
    return out


def _reprise_selection(study: Study = STUDY) -> dict | None:
    """``stratum -> (share_new, {region_id: subpop})`` of the resumed draw,
    or None before it (record corpus/404, option E)."""
    from .strata import STRATA_PATH
    path = study.path(STRATA_PATH)
    if not path.exists():
        return None
    rp = json.loads(path.read_text()).get("reprise")
    if not rp:
        return None
    return {k: (s["share_new"],
                {e["region_id"]: e["subpop"] for e in s["selection"]})
            for k, s in rp["strata"].items()}


def _weighted_median(values_weights: list[tuple[float, float]]):
    pairs = sorted((v, w) for v, w in values_weights if v is not None)
    total = sum(w for _, w in pairs)
    if not pairs or total == 0:
        return None
    acc = 0.0
    for v, w in pairs:
        acc += w
        if acc >= total / 2:
            return v
    return pairs[-1][0]


def _weighted(sub: list[dict], comparable: list[dict], share: float,
              subpop: dict, decided: list[dict]) -> dict:
    """Step 4 of the resumed draw: the part of the stratum the first
    analyser saw and the part only the new one sees weigh ``1 − f`` and
    ``f``, each estimated on its own regions — the reduction on the measured
    pairs, the rate of expressibility on every ``decided`` outcome."""
    from .reprise import weighted_rate

    def split(rows):
        return {"both": [p for p in rows
                         if subpop.get(p["region_id"]) != "new"],
                "new": [p for p in rows
                        if subpop.get(p["region_id"]) == "new"]}
    parts, outcome_parts = split(sub), split(decided)

    def rate(ps):
        return (sum(1 for p in ps if p.get("classification") in EXPRESSIBLE)
                / len(ps) if ps else None)
    weight = {"both": (1 - share), "new": share}
    vw = []
    for name, ps in parts.items():
        comp = [p for p in ps if p in comparable]
        for p in comp:
            vw.append((_reduction(p, "tokens"), weight[name] / len(comp)))
    return {
        "share_new": share,
        "n_both": len(parts["both"]), "n_new": len(parts["new"]),
        "expressible_rate": weighted_rate(rate(outcome_parts["both"]),
                                          rate(outcome_parts["new"]), share),
        "tokens_reduction_median": _weighted_median(vw),
    }


#: The four readings of a pair with optimized artefacts (record corpus/403):
#: the faithful translation, the careful rereading of the Python, the
#: notation on top of it, and both.
OPTIMIZED_STEPS = {
    "faithful": ("python", "ldpy"),
    "care": ("python", "optimized_python"),
    "notation": ("optimized_python", "optimized_ldpy"),
    "total": ("python", "optimized_ldpy"),
    # the header variant: the extracted header optimized too
    "care_header": ("python", "header_python"),
    "notation_header": ("header_python", "header_ldpy"),
    "total_header": ("python", "header_ldpy"),
}


def _optimized(ok: list[dict]) -> dict:
    """Rereading against notation, on the pairs that carry the optimized
    artefacts: token reduction of each step, on all tokens and on the host
    code alone (RDF text in strings and s{ } bodies counted apart, record
    corpus/403), overall and per stratum."""
    sub = [p for p in ok if "optimized_python" in p and "optimized_ldpy" in p]

    def steps(rows):
        out = {"n": len(rows)}
        for metric in ("tokens", "tokens_host"):
            out[metric] = {}
            for step, (a, b) in OPTIMIZED_STEPS.items():
                vals = []
                for p in rows:
                    if a not in p or b not in p:
                        continue
                    x, y = p[a].get(metric), p[b].get(metric)
                    if x:
                        vals.append(round(100.0 * (x - y) / x, 3))
                out[metric][step] = _dist(vals)
        return out
    result = steps(sub)
    # the stratum each region was drawn for (scripts/draw_optimize.py), else
    # the one it is filed under
    drawn = {}
    path = RESULTS_RAW / "optimize_sample.json"
    if path.exists():
        for k, regions in json.loads(path.read_text())["strata"].items():
            for e in regions:
                drawn[e["region_id"]] = k
    of = {p["region_id"]: drawn.get(p["region_id"], p.get("stratum"))
          for p in sub}
    result["by_stratum"] = {
        k: steps([p for p in sub if of[p["region_id"]] == k])
        for k in sorted(set(of.values()))}
    return result


def _by_construction(ok: list[dict]) -> dict:
    """How often each island of the language actually served, and where.

    This is what lets a construction be credited or debited on its own
    rather than hidden inside a global average.  A construction a pair does
    not attest (``constructions.uncredited``) is not credited to that pair:
    ``_unattested`` counts it.
    """
    credited = {id(p): set(p.get("constructions", []))
                - _uncredited(p) for p in ok}
    out: dict = {}
    for c in sorted(set().union(*credited.values()) if credited else ()):
        sub = [p for p in ok if c in credited[id(p)]]
        out[c] = {
            "pairs": len(sub),
            "repositories": len({p["repository"] for p in sub}),
            "strata": sorted({s for p in sub for s in p.get("strata", [])}),
            "tokens_reduction_pct": _dist([_reduction(p, "tokens") for p in sub]),
        }
    return out


def _uncredited(pair: dict) -> set:
    from .constructions import uncredited
    # a pair measured before the field existed is not credited
    return uncredited(pair.get("constructions", []),
                      pair.get("written_export", True))


def _unattested(ok: list[dict]) -> dict:
    """What ``_by_construction`` leaves out, so nothing is dropped silently."""
    from .constructions import UNATTESTED
    return {c: {"pairs": len([p for p in ok if c in _uncredited(p)]),
                "stratum": stratum, "reason": reason}
            for c, (stratum, reason) in UNATTESTED.items()}


def _band_csv(agg: dict, study: Study = STUDY) -> None:
    import csv
    with open(study.path(RESULTS_SUMMARY / "aggregate_bands.csv"), "w",
              newline="") as f:
        w = csv.writer(f)
        w.writerow([study.group, "n"]
                   + [f"{m}_median_reduction_pct" for m in METRICS])
        for band, d in agg["by_band"].items():
            w.writerow([band, d["n"]] +
                       [(d[m] or {}).get("median") for m in METRICS])
    if "by_construction" not in agg:
        return
    with open(study.path(RESULTS_SUMMARY / "aggregate_constructions.csv"), "w",
              newline="") as f:
        w = csv.writer(f)
        w.writerow(["construction", "pairs", "repositories",
                    "tokens_median_reduction_pct", "strata"])
        for c, d in agg["by_construction"].items():
            w.writerow([c, d["pairs"], d["repositories"],
                        (d["tokens_reduction_pct"] or {}).get("median"),
                        " ".join(d["strata"])])


def _figures(ok: list[dict], agg: dict, study: Study = STUDY) -> None:
    if not ok:
        return
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # 1. reduction per metric, split by where the RDF lives in the original.
    #    Pooling the subgroups would hide the finding: the notation acts on
    #    inline construction and is a no-op elsewhere.
    order = ["inline-construction", "terms-only", "string-embedded",
             "no-source-rdf"]
    subgroups = [s for s in order if any(p.get("subgroup") == s for p in ok)]
    if not subgroups:
        # Early in a campaign nothing is classified yet: there is no figure
        # to draw, and drawing an empty one would be worse than none.
        print("  (no subgroup classified yet: figures skipped)")
        return
    fig, axes = plt.subplots(1, len(subgroups), figsize=(2.4 * len(subgroups), 3.4),
                             sharey=True)
    if len(subgroups) == 1:
        axes = [axes]
    for ax, sg in zip(axes, subgroups):
        sub = [p for p in ok if p.get("subgroup") == sg]
        data = [[_reduction(p, m) for p in sub if _reduction(p, m) is not None]
                for m in METRICS]
        ax.boxplot(data, tick_labels=["LOC", "tok", "chr", "AST"])
        ax.axhline(0, color="grey", lw=0.5)
        ax.set_title(f"{sg}\n(n={len(sub)})", fontsize=8)
    axes[0].set_ylabel("reduction (%)")
    axes[0].set_ylim(-60, 70)
    fig.suptitle("LD Python vs RDFLib Python — surface reduction by where "
                 "the RDF is written", fontsize=9)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(study.path(RESULTS_SUMMARY / f"fig_reduction.{ext}"), dpi=150)
    plt.close(fig)

    # 2. triples written in the source vs token reduction
    fig, ax = plt.subplots(figsize=(6, 3.2))
    colors = {"inline-construction": "tab:red", "terms-only": "tab:orange",
              "string-embedded": "tab:blue", "no-source-rdf": "tab:grey"}
    for sg, color in colors.items():
        sub = [p for p in ok if p.get("subgroup") == sg]
        xs = [p["python"]["triples_added"] for p in sub]
        ys = [_reduction(p, "tokens") for p in sub]
        if xs:
            ax.scatter(xs, ys, label=f"{sg} (n={len(sub)})", color=color, s=20)
    ax.axhline(0, color="grey", lw=0.5)
    ax.set_xscale("symlog")
    ax.set_ylim(-60, 70)
    ax.set_xlabel("triples constructed in the original source (symlog)")
    ax.set_ylabel("token reduction (%)")
    ax.legend(fontsize=7)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(study.path(RESULTS_SUMMARY / f"fig_density_benefit.{ext}"), dpi=150)
    plt.close(fig)

    # 3. correspondence: scaffolding tokens per triple, paired
    fig, ax = plt.subplots(figsize=(6, 3.2))
    py = [p["python"].get("corr_scaffolding_tokens_per_triple") for p in ok]
    ld = [p["ldpy"].get("corr_scaffolding_tokens_per_triple") for p in ok]
    both = [(a, b) for a, b in zip(py, ld) if a is not None and b is not None]
    for i, (a, b) in enumerate(both):
        ax.plot([0, 1], [a, b], color="grey", lw=0.6, alpha=0.6)
    ax.scatter([0] * len(both), [a for a, _ in both], color="tab:blue", zorder=3)
    ax.scatter([1] * len(both), [b for _, b in both], color="tab:green", zorder=3)
    ax.set_xticks([0, 1], ["RDFLib Python", "LD Python"])
    ax.set_ylabel("scaffolding tokens per triple")
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(study.path(RESULTS_SUMMARY / f"fig_correspondence.{ext}"), dpi=150)
    plt.close(fig)

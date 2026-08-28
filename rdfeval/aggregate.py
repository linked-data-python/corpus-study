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
from .config import RESULTS_SUMMARY, provenance
from .stats import paired_report
from .study import Study, STUDY_401

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


def run(config: dict, study: Study = STUDY_401) -> None:
    pairs = load_pairs(study)
    translated = len(pairs)
    if study.incremental_review:
        # Fiche 403: the published aggregates are recomputed on demand over
        # the APPROVED subset only, and always say over how many.  A draft an
        # agent produced is a hypothesis, not a measurement.
        approved = [p for p in pairs if p.get("review_status") == "approved"]
        print(f"aggregate: {len(approved)} approved of {translated} translated")
        pairs = approved
    ok = [p for p in pairs if p["validation_status"] == "equivalent"]
    other = [p for p in pairs if p["validation_status"] != "equivalent"]

    agg: dict = {"provenance": provenance(config),
                 "study": study.name,
                 "pairs_translated": translated,
                 "pairs_reviewed_basis": ("approved" if study.incremental_review
                                          else "all final"),
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
        agg["by_stratum"] = _by_stratum(ok)
        agg["by_construction"] = _by_construction(ok)
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


def _by_stratum(ok: list[dict]) -> dict:
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
            "expressible": sum(1 for p in sub if p.get("classification") in
                               ("directly-expressible", "minor-restructuring")),
            "by_subgroup": {sg: len([p for p in sub if p.get("subgroup") == sg])
                            for sg in sorted({p.get("subgroup") for p in sub})},
            **{m: _dist([_reduction(p, m) for p in comparable])
               for m in METRICS},
            "string_embedded": {
                m: _dist([_reduction(p, m) for p in embedded]) for m in METRICS
            } if embedded else None,
        }
    return out


def _by_construction(ok: list[dict]) -> dict:
    """How often each island of the language actually served, and where.

    This is what lets a construction be credited or debited on its own
    rather than hidden inside a global average.
    """
    out: dict = {}
    for c in sorted({c for p in ok for c in p.get("constructions", [])}):
        sub = [p for p in ok if c in p.get("constructions", [])]
        out[c] = {
            "pairs": len(sub),
            "repositories": len({p["repository"] for p in sub}),
            "strata": sorted({s for p in sub for s in p.get("strata", [])}),
            "tokens_reduction_pct": _dist([_reduction(p, "tokens") for p in sub]),
        }
    return out


def _band_csv(agg: dict, study: Study = STUDY_401) -> None:
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


def _figures(ok: list[dict], agg: dict, study: Study = STUDY_401) -> None:
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

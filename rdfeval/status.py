"""Where a translation campaign stands, per stratum.

    python -m rdfeval status

Reads every example's ``meta.json`` and ``review.json`` and reports, for each
stratum: how many regions are drafted, final, machine-checked, and approved.
It is what drives the next batch — and what keeps the published numbers
honest, since the aggregates are computed on the approved subset
only (design record corpus/403).

``--check`` additionally runs the two machine checks on every pair marked
final, which is slower but tells you whether "final" is actually true.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict

from .config import RESULTS_SUMMARY
from .constructions import normalise as normalise_constructions
from .study import Study, STUDY
from .validate import iter_examples

STATUS_CSV = RESULTS_SUMMARY / "campaign_status.csv"


def collect(study: Study, run_checks: bool = False) -> dict:
    from .check import check

    per_group: dict[str, Counter] = defaultdict(Counter)
    # A region is FILED under its first stratum but CREDITED to every stratum
    # it belongs to (fiche 404): both counts are reported, or the directory
    # listing would read as a shortfall in the draw.
    credited: Counter = Counter()
    credited_final: Counter = Counter()
    classifications: dict[str, Counter] = defaultdict(Counter)
    constructions: Counter = Counter()
    outside: Counter = Counter()      # labels the vocabulary cannot place
    # What became of every drawn region.  A region a translator could not
    # RUN (a live service, a package that will not install) is not evidence
    # that the notation covers it, and it must not silently leave the
    # denominator: coverage is a share of what was ATTEMPTED.
    outcome: Counter = Counter()
    failures: list[tuple[str, str]] = []
    for ex_dir, meta in iter_examples(study):
        group = meta.get(study.group, "?")
        c = per_group[group]
        c["regions"] += 1
        c[meta.get("translation_status", "draft")] += 1
        classifications[group][meta.get("classification") or "unclassified"] += 1
        named, unknown = normalise_constructions(meta.get("constructions", []))
        for construction in named:
            constructions[construction] += 1
        for label in unknown:
            outside[label] += 1
        for stratum in meta.get("strata", []) or [group]:
            credited[stratum] += 1
            if meta.get("translation_status") == "final":
                credited_final[stratum] += 1
        status_ = meta.get("translation_status")
        classification = meta.get("classification")
        if status_ == "draft" and classification is None:
            outcome["not attempted"] += 1
        elif classification in ("excluded",):
            outcome["attempted, not evaluable"] += 1
        elif classification in ("directly-expressible", "minor-restructuring"):
            outcome["expressible"] += 1
        elif classification in ("awkward", "not-expressible"):
            outcome[classification] += 1
        else:
            outcome["in progress"] += 1
        review = ex_dir / "review.json"
        if review.exists():
            import json
            try:
                c[json.loads(review.read_text()).get("review_status",
                                                     "unreviewed")] += 1
            except (OSError, ValueError):
                c["unreadable-review"] += 1
        if run_checks and meta.get("translation_status") == "final":
            result = check(ex_dir)
            c["check-ok" if result["ok"] else "check-fail"] += 1
            if not result["ok"]:
                failures.append((meta["region_id"],
                                 (result["error"] or "")[:200]))
    return {"per_group": {k: dict(v) for k, v in sorted(per_group.items())},
            "credited": dict(credited),
            "credited_final": dict(credited_final),
            "classifications": {k: dict(v) for k, v in
                                sorted(classifications.items())},
            "outcome": dict(outcome),
            "constructions": dict(constructions.most_common()),
            "outside_vocabulary": dict(outside.most_common()),
            "failures": failures}


def run(config: dict, study: Study = STUDY, run_checks: bool = False) -> None:
    data = collect(study, run_checks)
    if not data["per_group"]:
        print(f"status: no example under {study.examples_dir}")
        return
    header = (f"{study.group:24s} {'filed':>6} {'credit':>6} "
              f"{'final':>6} {'approved':>8}")
    if run_checks:
        header += f" {'check OK':>8} {'FAIL':>5}"
    print(header)
    totals: Counter = Counter()
    for group, counts in data["per_group"].items():
        totals.update(counts)
        line = (f"{group:24s} {counts.get('regions', 0):6d} "
                f"{data['credited'].get(group, 0):6d} "
                f"{counts.get('final', 0):6d} {counts.get('approved', 0):8d}")
        if run_checks:
            line += (f" {counts.get('check-ok', 0):8d} "
                     f"{counts.get('check-fail', 0):5d}")
        print(line)
    print(f"{'TOTAL':24s} {totals['regions']:6d} {'':6s} "
          f"{totals['final']:6d} {totals['approved']:8d}"
          + (f" {totals['check-ok']:8d} {totals['check-fail']:5d}"
             if run_checks else ""))
    attempted = sum(v for k, v in data["outcome"].items()
                    if k != "not attempted")
    if attempted:
        print(f"\nwhat became of every drawn region ({attempted} attempted "
              f"of {sum(data['outcome'].values())} drawn):")
        for key in ("expressible", "awkward", "not-expressible",
                    "attempted, not evaluable", "in progress", "not attempted"):
            if data["outcome"].get(key):
                print(f"  {key:26s} {data['outcome'][key]:5d}")
        evaluable = attempted - data["outcome"].get("attempted, not evaluable", 0)
        if evaluable:
            print(f"  -> coverage: {data['outcome'].get('expressible', 0)}"
                  f"/{evaluable} of the regions that could be evaluated")
    if data["constructions"]:
        print("\nconstructions employed (declared in meta.json):")
        for name, n in data["constructions"].items():
            print(f"  {name:24s} {n:5d}")
    if data["outside_vocabulary"]:
        print("\noutside the controlled vocabulary (typo, or a construction "
              "the vocabulary is missing):")
        for name, n in data["outside_vocabulary"].items():
            print(f"  {name!r}: {n}")
    for rid, err in data["failures"]:
        print(f"  ! {rid}: {err}")

    STATUS_CSV.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted({k for c in data["per_group"].values() for k in c})
    with open(study.path(STATUS_CSV), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([study.group] + keys)
        for group, counts in data["per_group"].items():
            w.writerow([group] + [counts.get(k, 0) for k in keys])

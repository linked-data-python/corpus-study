"""Small statistics toolkit (pure Python — no scipy dependency).

The evaluation is paired by construction: every example yields one RDFLib
measurement and one LD Python measurement of the same program.  Paired,
distribution-free procedures are therefore the appropriate default:

wilcoxon_signed_rank
    Two-sided Wilcoxon signed-rank test on the paired differences, with
    zero-difference pairs dropped (Wilcoxon's original treatment), average
    ranks for ties, and a normal approximation with continuity and tie
    corrections.  Exact for the purposes here (n is small but the normal
    approximation is used consistently and reported as such); the p-value
    is a *descriptive* statistic — no conclusion is hard-coded anywhere in
    this pipeline.

cliffs_delta
    Non-parametric effect size in [-1, 1]: the probability that a value
    from one sample exceeds a value from the other, minus the reverse.

bootstrap_ci
    Percentile bootstrap confidence interval of any statistic, with a
    fixed seed so every reported interval is reproducible.

hodges_lehmann
    Median of pairwise differences — a robust location estimate for the
    paired shift, reported alongside the median reduction.
"""

from __future__ import annotations

import math
import random
import statistics as st


def _ranks(values: list[float]) -> list[float]:
    """Average ranks (1-based) of the values."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def _normal_sf(z: float) -> float:
    """Upper-tail probability of the standard normal distribution."""
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def wilcoxon_signed_rank(xs: list[float], ys: list[float]) -> dict:
    """Two-sided Wilcoxon signed-rank test for paired samples."""
    if len(xs) != len(ys):
        raise ValueError("paired samples must have equal length")
    diffs = [x - y for x, y in zip(xs, ys)]
    nonzero = [d for d in diffs if d != 0]
    n = len(nonzero)
    if n == 0:
        return {"n": 0, "n_zero": len(diffs), "W": None, "z": None,
                "p_two_sided": None, "method": "wilcoxon-signed-rank"}
    ranks = _ranks([abs(d) for d in nonzero])
    w_plus = sum(r for d, r in zip(nonzero, ranks) if d > 0)
    w_minus = sum(r for d, r in zip(nonzero, ranks) if d < 0)
    w = min(w_plus, w_minus)
    mean_w = n * (n + 1) / 4.0
    # tie correction on the ranks of |d|
    tie_term = 0.0
    counts: dict[float, int] = {}
    for r in ranks:
        counts[r] = counts.get(r, 0) + 1
    for c in counts.values():
        if c > 1:
            tie_term += c ** 3 - c
    var_w = (n * (n + 1) * (2 * n + 1) - tie_term / 2.0) / 24.0
    if var_w <= 0:
        return {"n": n, "n_zero": len(diffs) - n, "W": w, "z": None,
                "p_two_sided": None, "method": "wilcoxon-signed-rank"}
    z = (w - mean_w + 0.5) / math.sqrt(var_w)   # continuity correction
    p = 2.0 * _normal_sf(abs(z))
    return {"n": n, "n_zero": len(diffs) - n, "W": round(w, 3),
            "W_plus": round(w_plus, 3), "W_minus": round(w_minus, 3),
            "z": round(z, 4), "p_two_sided": min(1.0, round(p, 6)),
            "method": "wilcoxon-signed-rank (normal approx., "
                      "continuity + tie corrected)"}


def cliffs_delta(xs: list[float], ys: list[float]) -> dict:
    """Cliff's delta effect size with the usual magnitude labels."""
    if not xs or not ys:
        return {"delta": None, "magnitude": None}
    gt = lt = 0
    for x in xs:
        for y in ys:
            if x > y:
                gt += 1
            elif x < y:
                lt += 1
    delta = (gt - lt) / (len(xs) * len(ys))
    a = abs(delta)
    magnitude = ("negligible" if a < 0.147 else
                 "small" if a < 0.33 else
                 "medium" if a < 0.474 else "large")
    return {"delta": round(delta, 4), "magnitude": magnitude}


def hodges_lehmann(diffs: list[float]) -> float | None:
    """Median of the Walsh averages of the paired differences."""
    if not diffs:
        return None
    walsh = [(diffs[i] + diffs[j]) / 2.0
             for i in range(len(diffs)) for j in range(i, len(diffs))]
    return round(st.median(walsh), 4)


def bootstrap_ci(values: list[float], statistic=st.median,
                 n_resamples: int = 10000, seed: int = 20260827,
                 alpha: float = 0.05) -> dict | None:
    """Percentile bootstrap CI of `statistic` (deterministic given the seed)."""
    vals = [v for v in values if v is not None]
    if len(vals) < 2:
        return None
    rng = random.Random(seed)
    stats_ = []
    n = len(vals)
    for _ in range(n_resamples):
        sample = [vals[rng.randrange(n)] for _ in range(n)]
        stats_.append(statistic(sample))
    stats_.sort()
    lo = stats_[int((alpha / 2) * n_resamples)]
    hi = stats_[min(n_resamples - 1, int((1 - alpha / 2) * n_resamples))]
    return {"point": round(statistic(vals), 4), "lo": round(lo, 4),
            "hi": round(hi, 4), "level": 1 - alpha,
            "method": f"percentile bootstrap, {n_resamples} resamples, seed {seed}"}


def paired_report(xs: list[float], ys: list[float]) -> dict | None:
    """Full paired comparison of two aligned measurement vectors."""
    pairs = [(x, y) for x, y in zip(xs, ys)
             if x is not None and y is not None]
    if len(pairs) < 2:
        return None
    a = [p[0] for p in pairs]
    b = [p[1] for p in pairs]
    diffs = [x - y for x, y in pairs]
    return {
        "n_pairs": len(pairs),
        "median_a": round(st.median(a), 4),
        "median_b": round(st.median(b), 4),
        "median_difference": round(st.median(diffs), 4),
        "hodges_lehmann_shift": hodges_lehmann(diffs),
        "difference_ci": bootstrap_ci(diffs),
        "wilcoxon": wilcoxon_signed_rank(a, b),
        "cliffs_delta": cliffs_delta(a, b),
    }

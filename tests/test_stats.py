"""Tests of the paired-statistics toolkit (values checked against known cases)."""

import statistics as st

from rdfeval.stats import (bootstrap_ci, cliffs_delta, hodges_lehmann,
                           paired_report, wilcoxon_signed_rank)


def test_wilcoxon_hand_computed_case():
    """Hand-computed: differences 15,-7,5,20,0,-9,17,-12,5,-10.

    The zero pair is dropped (n=9); |d| ranks with the 5,5 tie averaged to
    1.5 give W+ = 7+1.5+9+8+1.5 = 27 and W- = 3+4+6+5 = 18 (sum 45 =
    n(n+1)/2), so W = 18 and the shift is not significant.
    """
    a = [125, 115, 130, 140, 140, 115, 140, 125, 140, 135]
    b = [110, 122, 125, 120, 140, 124, 123, 137, 135, 145]
    res = wilcoxon_signed_rank(a, b)
    assert res["n"] == 9            # one zero difference dropped
    assert res["n_zero"] == 1
    assert res["W_plus"] == 27.0
    assert res["W_minus"] == 18.0
    assert res["W"] == 18.0
    assert res["p_two_sided"] > 0.5


def test_wilcoxon_all_zero_differences():
    res = wilcoxon_signed_rank([1, 2, 3], [1, 2, 3])
    assert res["n"] == 0 and res["W"] is None and res["p_two_sided"] is None


def test_wilcoxon_perfect_separation_is_significant():
    a = list(range(20, 40))
    b = [x - 5 for x in a]
    res = wilcoxon_signed_rank(a, b)
    assert res["W"] == 0.0
    assert res["p_two_sided"] < 0.001


def test_cliffs_delta_extremes_and_labels():
    assert cliffs_delta([5, 6, 7], [1, 2, 3])["delta"] == 1.0
    assert cliffs_delta([1, 2, 3], [5, 6, 7])["delta"] == -1.0
    assert cliffs_delta([1, 2, 3], [1, 2, 3])["magnitude"] == "negligible"
    assert cliffs_delta([5, 6, 7], [1, 2, 3])["magnitude"] == "large"


def test_hodges_lehmann_shift():
    assert hodges_lehmann([2.0, 4.0, 6.0]) == 4.0
    assert hodges_lehmann([]) is None


def test_bootstrap_ci_deterministic_and_brackets_median():
    values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    ci1 = bootstrap_ci(values, n_resamples=2000)
    ci2 = bootstrap_ci(values, n_resamples=2000)
    assert ci1 == ci2                      # same seed -> same interval
    assert ci1["lo"] <= st.median(values) <= ci1["hi"]


def test_bootstrap_ci_too_few_values():
    assert bootstrap_ci([1]) is None


def test_paired_report_structure():
    a = [10, 12, 14, 16, 18]
    b = [5, 7, 6, 9, 8]
    rep = paired_report(a, b)
    assert rep["n_pairs"] == 5
    assert rep["median_difference"] > 0
    assert rep["wilcoxon"]["p_two_sided"] is not None
    assert rep["cliffs_delta"]["delta"] == 1.0
    assert rep["difference_ci"]["lo"] <= rep["median_difference"] <= rep["difference_ci"]["hi"]


def test_paired_report_skips_missing_values():
    rep = paired_report([1, None, 3, 4], [0, 1, None, 2])
    assert rep["n_pairs"] == 2

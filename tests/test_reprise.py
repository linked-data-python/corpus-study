"""The resumed draw (records corpus/403, 404, option E)."""

from rdfeval.reprise import keeps_stratum, weighted_rate


def test_a_region_keeps_its_stratum_by_its_recorded_site_or_its_lines():
    region = {"repository": "r/r", "path": "a.py", "lineno": 10,
              "end_lineno": 20, "sites": [{"kind": "ns_import_project",
                                           "line": 2}]}
    index = {("ns_import_project", "r/r", "a.py"): {2},
             ("remove", "r/r", "a.py"): {15},
             ("trav_existence", "r/r", "a.py"): {30}}
    assert keeps_stratum(region, "ns_import_project", index)   # recorded
    assert keeps_stratum(region, "remove", index)              # in its lines
    assert not keeps_stratum(region, "trav_existence", index)  # outside


def test_a_rate_is_weighted_by_the_share_of_new_sites():
    assert weighted_rate(0.8, 0.4, 0.25) == 0.8 * 0.75 + 0.4 * 0.25
    assert weighted_rate(0.8, None, 0.0) == 0.8
    assert weighted_rate(None, 0.5, 0.9) == 0.5


def test_the_weighted_median_follows_the_weights():
    from rdfeval.aggregate import _weighted_median
    assert _weighted_median([(1, 0.1), (5, 0.1), (9, 0.8)]) == 9
    assert _weighted_median([(1, 0.5), (5, 0.25), (9, 0.25)]) == 1
    assert _weighted_median([]) is None


def test_a_stratum_counts_only_its_resumed_selection_and_is_weighted():
    from rdfeval.aggregate import _by_stratum

    def pair(rid, cls, ldpy_tokens):
        return {"region_id": rid, "repository": "o/r", "strata": ["remove"],
                "subgroup": "inline-construction", "classification": cls,
                "python": {"code_loc": 10, "tokens": 100, "chars": 100,
                           "syntax_nodes": 50},
                "ldpy": {"code_loc": 10, "tokens": ldpy_tokens, "chars": 100,
                         "syntax_nodes": 40}}
    pairs = [pair("old", "directly-expressible", 80),
             pair("new", "not-expressible", 100),
             pair("gone", "directly-expressible", 10)]   # lost the stratum
    agg = _by_stratum(pairs, {"remove": (0.25, {"old": "both",
                                                "new": "new"})})
    st = agg["remove"]
    assert st["n"] == 2
    w = st["weighted"]
    assert (w["n_both"], w["n_new"]) == (1, 1)
    assert w["expressible_rate"] == 0.75
    assert w["tokens_reduction_median"] == 20.0


def test_a_not_expressible_region_lowers_the_rate_though_never_measured():
    """`compare` measures no `not-expressible` region: read on the pairs
    alone, every stratum would look expressible."""
    from rdfeval.aggregate import _by_stratum

    measured = [{"region_id": "a", "repository": "o/r",
                 "strata": ["remove"], "subgroup": "inline-construction",
                 "classification": "directly-expressible",
                 "python": {"code_loc": 10, "tokens": 100, "chars": 100,
                            "syntax_nodes": 50},
                 "ldpy": {"code_loc": 10, "tokens": 80, "chars": 100,
                          "syntax_nodes": 40}}]
    outcomes = [{"region_id": "a", "strata": ["remove"],
                 "classification": "directly-expressible"},
                {"region_id": "b", "strata": ["remove"],
                 "classification": "not-expressible"},
                {"region_id": "c", "strata": ["remove"],
                 "classification": "not-expressible"}]   # not selected
    agg = _by_stratum(measured, {"remove": (0.0, {"a": "both", "b": "both"})},
                      outcomes)
    st = agg["remove"]
    assert st["coverage"] == {"finals": 2, "expressible": 1,
                              "not_expressible": 1}
    assert st["weighted"]["expressible_rate"] == 0.5
    assert st["weighted"]["tokens_reduction_median"] == 20.0


def test_a_final_pair_left_out_of_the_selection_is_not_published(
        tmp_path, monkeypatch):
    import json
    from rdfeval import aggregate
    from rdfeval.study import STUDY

    def pair(rid):
        return {"region_id": rid, "repository": "o/r", "path": "m.py",
                "stratum": "remove", "strata": ["remove"],
                "constructions": ["-{ }"], "oracle": "isomorphism",
                "review_status": "approved", "validation_status": "equivalent",
                "classification": "directly-expressible",
                "subgroup": "inline-construction",
                "python": {"code_loc": 10, "tokens": 100, "chars": 200,
                           "syntax_nodes": 50, "rdf_ops": 3, "islands": 0},
                "ldpy": {"code_loc": 6, "tokens": 60, "chars": 120,
                         "syntax_nodes": 30, "rdf_ops": 3, "islands": 1},
                "ratios": {}}
    monkeypatch.setattr(aggregate, "load_pairs",
                        lambda study: [pair("kept"), pair("left")])
    monkeypatch.setattr(aggregate, "_reprise_selection",
                        lambda study: {"remove": (0.0, {"kept": "both"})})
    monkeypatch.setattr(aggregate, "_outcomes", lambda study, force: [])
    monkeypatch.setattr(aggregate, "_figures", lambda ok, agg, study: None)
    monkeypatch.setattr(aggregate, "RESULTS_SUMMARY", tmp_path)
    aggregate.run({"meta": {"config_version": "1", "metrics_version": "1"}},
                  STUDY)
    agg = json.loads((tmp_path / "aggregate.json").read_text())
    assert agg["pairs_total"] == 1
    assert agg["pairs_outside_selection"] == ["left"]


def test_a_region_completed_into_another_stratum_is_credited_in_its_meta(
        tmp_path, monkeypatch):
    import json
    from rdfeval import reprise

    d = tmp_path / "remove" / "r"
    d.mkdir(parents=True)
    (d / "meta.json").write_text(json.dumps(
        {"region_id": "r", "strata": ["remove"]}))
    monkeypatch.setattr(reprise, "EXAMPLES_DIR", tmp_path)
    strata = {"remove": {"selection": [{"region_id": "r"}]},
              "bind_initbindings": {"selection": [{"region_id": "r"}]}}
    assert reprise.credit_metas(strata) == 1
    assert json.loads((d / "meta.json").read_text())["strata"] == [
        "remove", "bind_initbindings"]
    assert reprise.credit_metas(strata) == 0

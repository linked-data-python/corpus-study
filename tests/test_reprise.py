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

"""The three-artefact harness: optimized.py and optimized.ldpy (corpus/403)."""

import json

import pytest

from rdfeval.check import check_region
from rdfeval.compare import measure_optimized, measure_pair, python_side

ORIGINAL = """\
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import FOAF

EX = Namespace("http://example.org/")

g = Graph()
for who in ("alice", "bob"):
    node = EX[who]
    name = who.capitalize()
    g.add((node, FOAF.name, Literal(name)))
"""

TRANSLATED = """\
from rdflib import Graph
@prefix ex: <http://example.org/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

g = Graph()
@graph g
for who in ("alice", "bob"):
    node = ex:{who}
    name = who.capitalize()
    +{ {node} foaf:name {name} }
"""

OPTIMIZED_PY = """\
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import FOAF

EX = Namespace("http://example.org/")

g = Graph()
for who in ("alice", "bob"):
    g.add((EX[who], FOAF.name, Literal(who.capitalize())))
"""

OPTIMIZED_LDPY = """\
from rdflib import Graph
@prefix ex: <http://example.org/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

g = Graph()
@graph g
for who in ("alice", "bob"):
    +{ ex:{who} foaf:name {who.capitalize()} }
"""

DRIVER = "from rdfeval.harness import run_pair\nrun_pair(__file__)\n"


def _region(tmp_path, optimized_py=OPTIMIZED_PY, optimized_ldpy=OPTIMIZED_LDPY):
    ex = tmp_path / "region"
    ex.mkdir()
    (ex / "original.py").write_text(ORIGINAL)
    (ex / "translated.ldpy").write_text(TRANSLATED)
    (ex / "driver.py").write_text(DRIVER)
    if optimized_py is not None:
        (ex / "optimized.py").write_text(optimized_py)
    if optimized_ldpy is not None:
        (ex / "optimized.ldpy").write_text(optimized_ldpy)
    return ex


def test_without_optimized_artefacts_only_the_pair_is_checked(tmp_path):
    results = check_region(_region(tmp_path, None, None))
    assert [r["artefact"] for r in results] == ["translated.ldpy"]
    assert results[0]["ok"], results[0]["error"]


def test_each_optimized_artefact_is_proved_against_the_original(tmp_path):
    results = check_region(_region(tmp_path))
    assert [r["artefact"] for r in results] == \
        ["translated.ldpy", "optimized.py", "optimized.ldpy"]
    assert all(r["ok"] for r in results), [r["error"] for r in results]
    assert [r["verdict"]["sides"] for r in results] == [
        ["original.py", "translated.ldpy"],
        ["original.py", "optimized.py"],
        ["original.py", "optimized.ldpy"]]


@pytest.mark.parametrize("artefact", ["optimized.py", "optimized.ldpy"])
def test_a_wrong_optimized_artefact_fails(tmp_path, artefact):
    wrong = {"optimized.py": OPTIMIZED_PY.replace("capitalize", "upper"),
             "optimized.ldpy": OPTIMIZED_LDPY.replace("capitalize", "upper")}
    kwargs = {"optimized_py": OPTIMIZED_PY, "optimized_ldpy": OPTIMIZED_LDPY}
    kwargs[artefact.replace(".", "_")] = wrong[artefact]
    results = {r["artefact"]: r for r in check_region(_region(tmp_path, **kwargs))}
    assert not results[artefact]["ok"]
    others = [r for name, r in results.items() if name != artefact]
    assert all(r["ok"] for r in others)


def test_a_driver_that_ignores_the_sides_is_not_a_green(tmp_path):
    ex = _region(tmp_path)
    # a hand-rolled verdict that always proves the default pair
    (ex / "driver.py").write_text(
        "import json, sys\n"
        "print('RDFEVAL-VERDICT ' + json.dumps({'equivalent': True}),"
        " file=sys.stderr)\n")
    results = {r["artefact"]: r for r in check_region(ex)}
    assert not results["optimized.py"]["ok"]
    assert "not ['original.py', 'optimized.py']" in results["optimized.py"]["error"]


def test_optimized_ratios_separate_care_from_notation():
    py = python_side(ORIGINAL)
    opt = measure_optimized(py, OPTIMIZED_PY, OPTIMIZED_LDPY)
    assert opt["ratios_care"]["tokens"] < 1.0          # the rewrite alone
    assert opt["ratios_notation"]["tokens"] < 1.0      # the notation on top
    total = opt["ratios_total"]["tokens"]
    assert total == pytest.approx(
        opt["ratios_care"]["tokens"] * opt["ratios_notation"]["tokens"],
        abs=1e-3)
    # the faithful pair is measured exactly as before
    assert measure_pair(ORIGINAL, OPTIMIZED_LDPY)["python"] == py


def test_compare_skips_optimized_metrics_until_both_are_proved(tmp_path,
                                                               monkeypatch):
    from rdfeval import compare
    ex = _region(tmp_path)
    meta = {"region_id": "r", "repository": "o/r", "path": "p.py",
            "stratum": "s", "translation_status": "final",
            "classification": "directly-expressible",
            "optimization_status": "final",
            "validation_optimized": {
                "optimized.py": {"status": "equivalent"},
                "optimized.ldpy": {"status": "not-equivalent"}}}
    assert not compare._optimized_ready(meta)
    meta["validation_optimized"]["optimized.ldpy"]["status"] = "equivalent"
    assert compare._optimized_ready(meta)
    (ex / "meta.json").write_text(json.dumps(meta))
    # optimized.py must not be read as a context shim
    assert "optimized.py" in compare.NOT_SHIMS


def test_triage_ranks_high_first_and_distrusts_bad_files(tmp_path):
    from rdfeval import triage
    ex = tmp_path / "r"
    ex.mkdir()
    assert triage.read_triage(ex) is None
    (ex / "triage.json").write_text("{not json")
    assert triage.read_triage(ex)["priority"] == "high"
    (ex / "triage.json").write_text(json.dumps(
        {"priority": "urgent", "flags": ["made-up"], "questions": []}))
    t = triage.read_triage(ex)
    assert t["priority"] == "high" and t["unknown_flags"] == ["made-up"]


def test_a_hand_written_driver_is_redirected_by_the_helpers(tmp_path):
    ex = _region(tmp_path)
    (ex / "driver.py").write_text(
        "from pathlib import Path\n"
        "from rdfeval.harness import _exec_python, _exec_ldpy, _emit,"
        " graphs_isomorphic\n"
        "HERE = Path(__file__).resolve().parent\n"
        "ns_o, _ = _exec_python(HERE / 'original.py')\n"
        "ns_t, _ = _exec_ldpy(HERE / 'translated.ldpy')\n"
        "_emit({'equivalent': graphs_isomorphic(ns_o['g'], ns_t['g'])})\n")
    results = {r["artefact"]: r for r in check_region(ex)}
    assert all(r["ok"] for r in results.values()), \
        {k: r["error"] for k, r in results.items()}
    (ex / "optimized.py").write_text(
        OPTIMIZED_PY.replace("capitalize", "upper"))
    assert not {r["artefact"]: r for r in check_region(ex)}["optimized.py"]["ok"]


def test_a_driver_reading_files_itself_cannot_claim_the_sides(tmp_path):
    ex = _region(tmp_path)
    # reads translated.ldpy by hand: the redirection never applies
    (ex / "driver.py").write_text(
        "from rdfeval.harness import _emit\n"
        "open('translated.ldpy').read()\n"
        "_emit({'equivalent': True})\n")
    results = {r["artefact"]: r for r in check_region(ex)}
    assert results["translated.ldpy"]["ok"]       # what it was written for
    assert not results["optimized.ldpy"]["ok"]


def test_aggregate_separates_rereading_from_notation(monkeypatch, tmp_path):
    from rdfeval import aggregate
    monkeypatch.setattr(aggregate, "RESULTS_RAW", tmp_path)   # no sample file

    def side(tokens, host):
        return {"tokens": tokens, "tokens_host": host}
    pair = {"region_id": "r", "stratum": "remove",
            "python": side(100, 90), "ldpy": side(90, 80),
            "optimized_python": side(80, 70), "optimized_ldpy": side(60, 56)}
    out = aggregate._optimized([pair, {"region_id": "x", "python": {}}])
    assert out["n"] == 1
    assert out["tokens"]["care"]["median"] == 20.0
    assert out["tokens"]["notation"]["median"] == 25.0
    assert out["tokens"]["total"]["median"] == 40.0
    assert out["tokens"]["faithful"]["median"] == 10.0
    assert out["tokens_host"]["notation"]["median"] == 20.0
    assert out["by_stratum"]["remove"]["n"] == 1

"""The stratified draw by type of use (design record corpus/403)."""

import json

from rdfeval.strata import draw, region_for_site
from rdfeval.surface import STRATA

RCFG = {"max_region_loc": 120, "min_rdf_ops": 2, "coverage_threshold": 0.5}
SCFG = {"seed": 1, "target_per_stratum": 3, "max_per_repo_per_stratum": 2}

FILE = '''\
from rdflib import Graph, Namespace, RDF, Literal

EX = Namespace("http://example.org/")
g = Graph()


def build(rows):
    for row in rows:
        s = EX[row["id"]]
        g.add((s, RDF.type, EX.Thing))
        g.add((s, EX.value, Literal(row["v"])))


def read():
    return list(g.subjects(RDF.type, EX.Thing))
'''


def test_region_is_the_enclosing_function():
    r = region_for_site(FILE, 10, RCFG)
    assert r["kind"] == "function"
    assert r["qualname"] == "build"
    assert r["lineno"] == 7
    assert "g.add((s, EX.value" in r["source"]


def test_region_carries_the_bindings_it_reads_as_context():
    r = region_for_site(FILE, 10, RCFG)
    assert 'EX = Namespace("http://example.org/")' in r["context"]
    assert "g = Graph()" in r["context"]
    assert r["rdf_ops"] >= 2      # measured *with* that context


def test_a_module_level_site_of_a_small_file_is_the_whole_file():
    r = region_for_site(FILE, 3, RCFG)
    assert r["kind"] == "file"
    assert r["qualname"] == "<module>"


BIG = ("import os\n" * 200) + '''
from rdflib import Graph, Namespace, RDF
from myproject.vocab import BRICK

g = Graph()


def build():
    g.add((BRICK.a, RDF.type, BRICK.Thing))
    g.add((BRICK.b, RDF.type, BRICK.Thing))
'''


def test_a_declaration_site_is_rerouted_to_a_region_that_uses_it():
    """`from x import BRICK` alone carries no RDF operation: translating one
    line demonstrates nothing, so the region becomes a *user* of the name."""
    line = BIG.splitlines().index("from myproject.vocab import BRICK") + 1
    r = region_for_site(BIG, line, RCFG)
    assert r["qualname"] == "build"
    assert r["declaration_site_line"] == line
    assert "from myproject.vocab import BRICK" in r["context"]


def test_an_oversize_function_falls_back_to_the_enclosing_statement():
    src = "from rdflib import Graph, Namespace, RDF\nEX = Namespace('http://e/')\n" \
          "g = Graph()\n\ndef huge():\n" + \
          "".join(f"    x{i} = {i}\n" for i in range(200)) + \
          "    for i in range(3):\n" \
          "        g.add((EX.a, RDF.type, EX.C))\n" \
          "        g.add((EX.b, RDF.type, EX.C))\n"
    line = len(src.splitlines()) - 1
    r = region_for_site(src, line, RCFG)
    assert r["kind"] == "statement"
    assert r["source"].lstrip().startswith("for i in range(3):")
    assert r["loc"] <= RCFG["max_region_loc"]


# --- the draw ---------------------------------------------------------------

def _sites():
    out = []
    for repo in ("o/a", "o/b", "o/c"):
        for i in range(4):
            out.append({"repository": repo, "path": f"m{i}.py", "commit": "c",
                        "kind": "add_run_shared_subject", "line": 10,
                        "end_line": 11, "qualname": "build", "snippet": ""})
    return out


def _reader(repository, path):
    return FILE


def test_draw_is_capped_per_repository():
    result = draw(_sites(), SCFG, RCFG, {"o/a", "o/b", "o/c"}, _reader)
    st = result["strata"]["add_run_shared_subject"]
    assert st["drawn_regions"] == 3
    assert st["population_sites"] == 12
    repos = [r["repository"] for r in result["regions"].values()]
    assert max(repos.count(x) for x in set(repos)) <= SCFG["max_per_repo_per_stratum"]


def test_draw_is_deterministic():
    a = draw(_sites(), SCFG, RCFG, {"o/a", "o/b", "o/c"}, _reader)
    b = draw(_sites(), SCFG, RCFG, {"o/a", "o/b", "o/c"}, _reader)
    assert sorted(a["regions"]) == sorted(b["regions"])


def test_ineligible_repositories_are_never_drawn():
    result = draw(_sites(), SCFG, RCFG, {"o/a"}, _reader)
    assert {r["repository"] for r in result["regions"].values()} == {"o/a"}
    assert result["strata"]["add_run_shared_subject"]["population_sites"] == 4


def test_raising_the_target_tops_the_sample_up_instead_of_re_drawing():
    """The rule of `sample.draw_wave`: a reviewed translation stays valid."""
    first = draw(_sites(), SCFG, RCFG, {"o/a", "o/b", "o/c"}, _reader)
    bigger = {**SCFG, "target_per_stratum": 6, "max_per_repo_per_stratum": 4}
    second = draw(_sites(), bigger, RCFG, {"o/a", "o/b", "o/c"}, _reader,
                  previous=first["regions"])
    assert set(first["regions"]) <= set(second["regions"])
    assert second["strata"]["add_run_shared_subject"]["drawn_regions"] == 6


def test_a_region_drawn_for_two_strata_is_one_region_credited_twice():
    sites = _sites() + [{**s, "kind": "add_in_loop"} for s in _sites()]
    result = draw(sites, SCFG, RCFG, {"o/a", "o/b", "o/c"}, _reader)
    multi = [r for r in result["regions"].values() if len(r["strata"]) > 1]
    assert multi, "the same region should serve both strata"
    assert set(multi[0]["strata"]) == {"add_run_shared_subject", "add_in_loop"}


def test_every_stratum_appears_in_the_summary():
    result = draw([], SCFG, RCFG, set(), _reader)
    assert list(result["strata"]) == list(STRATA)
    assert all(st["drawn_regions"] == 0 for st in result["strata"].values())


# --- the two studies never share a number -----------------------------------

def test_study_output_paths_are_disjoint():
    from pathlib import Path
    from rdfeval.study import STUDY_401, STUDY_403, get
    base = Path("results/raw/pairs.jsonl")
    assert STUDY_401.path(base).name == "pairs.jsonl"
    assert STUDY_403.path(base).name == "pairs_403.jsonl"
    assert get("403").examples_dir.name == "examples403"
    assert get(None) is STUDY_401


def test_only_approved_pairs_enter_the_403_aggregates(tmp_path, monkeypatch):
    """Fiche 403: the published numbers are recomputed on the approved
    subset, and always say over how many."""
    import json
    from rdfeval import aggregate
    from rdfeval.study import STUDY_403

    def pair(rid, review):
        return {"region_id": rid, "repository": "o/r", "stratum": "remove",
                "strata": ["remove"], "constructions": ["-{ }"],
                "oracle": "isomorphism", "review_status": review,
                "classification": "directly-expressible",
                "validation_status": "equivalent",
                "python": {"code_loc": 10, "tokens": 100, "chars": 200,
                           "syntax_nodes": 50, "rdf_ops": 3, "islands": 0},
                "ldpy": {"code_loc": 6, "tokens": 60, "chars": 120,
                         "syntax_nodes": 30, "rdf_ops": 3, "islands": 1},
                "ratios": {}}

    monkeypatch.setattr(aggregate, "load_pairs", lambda study: [
        pair("a", "approved"), pair("b", "unreviewed"), pair("c", "rejected")])
    monkeypatch.setattr(aggregate, "RESULTS_SUMMARY", tmp_path)
    aggregate.run({"meta": {"config_version": "1", "metrics_version": "1"}},
                  STUDY_403)
    agg = json.loads((tmp_path / "aggregate_403.json").read_text())
    assert agg["pairs_translated"] == 3
    assert agg["pairs_total"] == 1
    assert agg["pairs_reviewed_basis"] == "approved"
    assert agg["by_stratum"]["remove"]["n"] == 1
    assert agg["by_construction"]["-{ }"]["pairs"] == 1


def test_check_reports_a_pair_that_does_not_transpile(tmp_path):
    from rdfeval.check import check
    (tmp_path / "translated.ldpy").write_text("x = ?\n")
    (tmp_path / "driver.py").write_text("")
    r = check(tmp_path)
    assert not r["ok"] and not r["transpiles"]
    assert "transpile:" in r["error"]


def test_check_passes_a_real_pair(tmp_path):
    from rdfeval.check import check
    (tmp_path / "original.py").write_text(
        "from rdflib import Graph, Namespace\n"
        "EX = Namespace('http://e/')\n"
        "g = Graph()\n"
        "g.add((EX.a, EX.p, EX.b))\n")
    (tmp_path / "translated.ldpy").write_text(
        "from rdflib import Graph\n"
        "@prefix ex: <http://e/> .\n"
        "@graph as g\n"
        "+{ ex:a ex:p ex:b }\n")
    (tmp_path / "driver.py").write_text(
        "from rdfeval.harness import run_pair\nVERDICT = run_pair(__file__)\n")
    r = check(tmp_path)
    assert r["transpiles"]
    assert r["ok"], r["error"]


def test_status_counts_filed_and_credited_separately(tmp_path, monkeypatch):
    """A region is filed under its first stratum but credited to each: the
    directory listing alone would read as a shortfall in the draw."""
    import json
    from rdfeval import status as status_mod

    def fake_examples(study):
        meta = {"region_id": "r1", "stratum": "remove",
                "strata": ["remove", "add_isolated"],
                "translation_status": "final", "classification": "awkward",
                "constructions": ["-{ }", "@graph"]}
        yield tmp_path, meta

    monkeypatch.setattr(status_mod, "iter_examples", fake_examples)
    (tmp_path / "review.json").write_text(json.dumps({"review_status": "approved"}))
    from rdfeval.study import STUDY_403
    data = status_mod.collect(STUDY_403)
    assert data["per_group"]["remove"]["regions"] == 1
    assert data["credited"] == {"remove": 1, "add_isolated": 1}
    assert data["per_group"]["remove"]["approved"] == 1
    assert data["constructions"] == {"-{ }": 1, "@graph": 1}


def test_article_export_takes_approved_pairs_only(tmp_path, monkeypatch):
    """Fiche 403: a published example comes from an approved pair — a draft
    an agent produced is a hypothesis, not something to print."""
    import json
    from rdfeval import article as article_mod
    from rdfeval.study import STUDY_403

    def make(rid, review, stratum="remove"):
        d = tmp_path / rid
        d.mkdir()
        (d / "review.json").write_text(json.dumps({"review_status": review}))
        (d / "original.py").write_text("# header\n\ng.remove((s, p, None))\n")
        (d / "translated.ldpy").write_text("# header\n\n-{ {s} {p} ?o }\n")
        return d, {"region_id": rid, "stratum": stratum, "strata": [stratum],
                   "repository": "o/r", "commit": "abc", "path": "m.py",
                   "qualname": "f", "lineno": 1, "end_lineno": 3,
                   "classification": "directly-expressible",
                   "constructions": ["-{ }"], "oracle": "isomorphism",
                   "translation_notes": []}

    examples = [make("ok", "approved"), make("draft", "unreviewed")]
    monkeypatch.setattr(article_mod, "iter_examples", lambda study: iter(examples))
    monkeypatch.setattr(article_mod, "ARTICLE_DIR", tmp_path / "out")
    monkeypatch.setattr(article_mod, "_licence_of", lambda repo: "MIT")
    article_mod.run({}, STUDY_403)
    page = (tmp_path / "out" / "remove.md").read_text()
    assert "-{ {s} {p} ?o }" in page
    assert "o/r" in page and "abc" in page and "MIT" in page
    assert "# header" not in page          # the provenance is stated in prose
    assert not (tmp_path / "out" / "trav_one_step.md").exists()


def test_construction_vocabulary_folds_the_ways_people_write_it():
    """`by_construction` is a headline measurement, so free text does not do:
    the first wave wrote one construction four ways."""
    from rdfeval.constructions import normalise
    named, unknown = normalise([
        "nom préfixé", "nom prefixe", "prefixed name",     # one construction
        "suffixe d'appel (g)", "call suffix (g)",          # one construction
        "f<...>", "f<…>",                                  # one construction
        "littéral typé", "litteral type",                  # one construction
    ])
    assert named == ["prefixed name", "call suffix (g)", "f<…>", "typed literal"]
    assert unknown == []


def test_an_unplaceable_label_is_reported_not_dropped():
    """A label outside the vocabulary is a typo to fix or a construction the
    vocabulary lacks — both must be visible."""
    from rdfeval.constructions import normalise
    named, unknown = normalise(["-{ }", "un truc que personne n'a défini"])
    assert named == ["-{ }"]
    assert unknown == ["un truc que personne n'a défini"]


def test_every_canonical_name_normalises_to_itself():
    from rdfeval.constructions import CONSTRUCTIONS, normalise
    named, unknown = normalise(CONSTRUCTIONS)
    assert unknown == []
    assert named == list(CONSTRUCTIONS)


def test_string_embedded_pairs_are_reported_apart_never_pooled():
    """RDF inside a Python string is ONE token to the tokenizer; making it
    visible multiplies the count for a reason that is not notation quality.
    A SPARQL stratum is string-embedded by nature."""
    from rdfeval.aggregate import _by_stratum
    def pair(rid, subgroup, py_tokens, ldpy_tokens):
        return {"region_id": rid, "repository": "o/r", "strata": ["sparql_literal"],
                "subgroup": subgroup, "classification": "directly-expressible",
                "python": {"code_loc": 10, "tokens": py_tokens, "chars": 100,
                           "syntax_nodes": 50},
                "ldpy": {"code_loc": 10, "tokens": ldpy_tokens, "chars": 100,
                         "syntax_nodes": 40}}
    agg = _by_stratum([pair("a", "inline-construction", 100, 80),
                       pair("b", "string-embedded", 100, 300)])
    st = agg["sparql_literal"]
    assert st["n"] == 2
    assert st["n_surface_comparable"] == 1 and st["n_string_embedded"] == 1
    assert st["tokens"]["median"] == 20.0, "the headline uses the comparable pair"
    assert st["string_embedded"]["tokens"]["median"] == -200.0


CTX_SOURCE = ("import os\n"
              "from rdflib import Graph, Namespace\n\n"
              "EX = Namespace('http://e/')\n"
              "bad = []\n"
              + "".join(f"x{i} = {i}\n" for i in range(60))
              + "g = Graph()\n"
                "for s in g.subjects(None, EX.p):\n"
                "    bad.append(s)\n"
                "    g.add((s, EX.q, EX.r))\n"
                "LATER = Namespace('http://later/')\n"
                "bad = [LATER.z]\n")
CTX_LINE = CTX_SOURCE.splitlines().index("for s in g.subjects(None, EX.p):") + 1
CTX_CFG = {"max_region_loc": 20, "min_rdf_ops": 2}


def test_a_statement_region_sees_only_what_precedes_it():
    """A later `bad = [LATER.z]` handed in as context REBINDS a name the
    region reads: the region would no longer start from the file's state."""
    r = region_for_site(CTX_SOURCE, CTX_LINE, CTX_CFG)
    assert r["kind"] == "statement"
    assert "bad = []" in r["context"]
    assert not any("LATER" in c for c in r["context"])


def test_context_lines_bring_their_own_dependencies():
    """`EX = Namespace(...)` needs `from rdflib import Namespace`, and the
    region never names `Namespace` itself."""
    r = region_for_site(CTX_SOURCE, CTX_LINE, CTX_CFG)
    assert "from rdflib import Graph, Namespace" in r["context"]
    assert "import os" not in r["context"]      # needed by nobody
    assert r["rdf_ops"] > 0, "with its bindings, the region is no longer blind"


def test_a_function_region_keeps_bindings_defined_after_it():
    """Python's own rule: a module-level name defined after a `def` is
    available when the function is called."""
    src = ("from rdflib import Graph, Namespace\n"
           "def build():\n"
           "    g = Graph()\n"
           "    g.add((EX.a, EX.p, EX.b))\n"
           "    g.add((EX.a, EX.q, EX.c))\n"
           "    return g\n"
           "EX = Namespace('http://e/')\n")
    r = region_for_site(src, 3, {"max_region_loc": 120, "min_rdf_ops": 2})
    assert r["kind"] == "function"
    assert "EX = Namespace('http://e/')" in r["context"]

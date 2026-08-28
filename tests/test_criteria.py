"""Repository inclusion criteria: the two stages, and vendored-tree detection."""

from __future__ import annotations

import pytest

from rdfeval.config import load_config
from rdfeval.criteria import is_vendored, stage1_reasons, stage2_reason


@pytest.fixture(scope="module")
def cfg():
    return load_config()["selection"]


@pytest.fixture(scope="module")
def acfg():
    return load_config()["analysis"]


def good(**over) -> dict:
    """A candidate that satisfies every stage-1 criterion."""
    rec = {
        "full_name": "example/rdf-tool",
        "description": "A tool that builds knowledge graphs",
        "topics": ["rdf", "sparql"],
        "languages": {"Python": 400_000, "HTML": 1_000},
        "commits": 250,
        "size_kb": 4_000,
        "last_commit": "2026-01-15T09:00:00Z",
        "licence": "MIT",
        "fork": False,
        "archived": False,
        "mirror": False,
        "template": False,
        "empty": False,
        "unavailable": False,
    }
    rec.update(over)
    return rec


def test_a_conforming_candidate_has_no_reason(cfg):
    assert stage1_reasons(good(), cfg) == []


@pytest.mark.parametrize("over, marker", [
    ({"unavailable": True}, "unavailable"),
    ({"empty": True}, "empty"),
    ({"fork": True}, "fork"),
    ({"mirror": True}, "mirror_or_template"),
    ({"template": True}, "mirror_or_template"),
    ({"languages": {"Python": 900}}, "python_bytes"),
    ({"languages": {"Go": 900_000}}, "python_bytes"),
    ({"commits": 3}, "commits"),
    ({"size_kb": 10}, "size<"),
    ({"size_kb": 900_000}, "size>"),
    ({"last_commit": "2016-04-02T00:00:00Z"}, "inactive_since"),
    ({"licence": None}, "licence="),
    ({"licence": "NOASSERTION"}, "licence="),
])
def test_each_criterion_rejects_and_says_why(cfg, over, marker):
    reasons = stage1_reasons(good(**over), cfg)
    assert any(marker in r for r in reasons), reasons


def test_teaching_material_is_matched_on_name_description_and_topics(cfg):
    assert "teaching_material" in stage1_reasons(
        good(full_name="uni/Curso2025-2026"), cfg)
    assert "teaching_material" in stage1_reasons(
        good(description="Exercise sheets for the semantic web course"), cfg)
    assert "teaching_material" in stage1_reasons(
        good(topics=["tutorial", "rdf"]), cfg)
    assert stage1_reasons(good(description="A discourse parser"), cfg) == []


def test_a_repository_named_after_the_library_is_the_library(cfg):
    assert "library_itself" in stage1_reasons(good(full_name="alcides/rdflib"), cfg)
    assert "library_itself" in stage1_reasons(good(full_name="x/RDFLib"), cfg)
    # ... but an RDF library written *against* rdflib is a user of it, and is
    # exactly the kind of code the study is about.
    assert stage1_reasons(good(full_name="RDFLib/pySHACL"), cfg) == []
    assert stage1_reasons(good(full_name="RDFLib/OWL-RL"), cfg) == []
    assert stage1_reasons(good(full_name="x/rdflib-endpoint"), cfg) == []


def test_missing_metadata_never_satisfies_a_criterion(cfg):
    reasons = stage1_reasons({"full_name": "a/b"}, cfg)
    assert any("python_bytes" in r for r in reasons)
    assert any("commits" in r for r in reasons)
    assert any("size<" in r for r in reasons)
    assert any("licence=" in r for r in reasons)


def test_stage2_prunes_only_on_evidence(cfg):
    analysed = {"python_files": 40, "rdf_files": 12, "analysis_errors": 0}
    assert stage2_reason(analysed, cfg) is None
    assert stage2_reason({}, cfg) is None                      # not analysed yet
    assert "rdf_files=0" in stage2_reason(
        {**analysed, "rdf_files": 0}, cfg)
    assert "python_files=1" in stage2_reason(
        {**analysed, "python_files": 1}, cfg)
    assert stage2_reason(
        {"python_files": 3, "rdf_files": 0, "analysis_errors": 3}, cfg) == \
        "all_files_unparsable"


def test_vendored_tree_detection(acfg):
    # The prophet case: rdflib copied at the root of an application repository.
    assert is_vendored(("rdflib", "plugins", "sparql", "sparql.py"),
                       "MKLab-ITI/prophet", acfg)
    assert is_vendored(("isodate", "isodates.py"), "MKLab-ITI/prophet", acfg)
    # ... but a project's own package is not vendored, whatever its name.
    assert not is_vendored(("SPARQLWrapper", "Wrapper.py"),
                           "RDFLib/sparqlwrapper", acfg)
    assert not is_vendored(("rdflib", "graph.py"), "alcides/rdflib", acfg)
    # Generic vendor directories are always third-party.
    assert is_vendored(("_vendor", "six.py"), "any/project", acfg)
    assert is_vendored(("third_party", "x.py"), "any/project", acfg)
    # Ordinary source is untouched.
    assert not is_vendored(("src", "app.py"), "any/project", acfg)
    assert not is_vendored((), "any/project", acfg)


def test_a_bundled_python_runtime_is_vendored(acfg):
    # `prrvchr/mContactOOo` ships setuptools, selenium and trio under
    # `uno/lib/python/` — a virtualenv layout without the site-packages marker.
    assert is_vendored(("uno", "lib", "python", "trio", "_core.py"),
                       "prrvchr/mContactOOo", acfg)
    assert is_vendored(("lib", "python3.11", "setuptools", "dist.py"),
                       "any/project", acfg)
    assert not is_vendored(("lib", "helpers.py"), "any/project", acfg)

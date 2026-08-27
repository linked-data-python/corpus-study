"""Tests of region extraction and band assignment."""

from rdfeval.regions import extract_regions
from rdfeval.sample import band_of

RCFG = {"min_rdf_ops": 2, "max_region_loc": 120, "coverage_threshold": 0.5}


def test_function_region_extracted_with_context():
    src = (
        "import sys\n"
        "from rdflib import Graph, Namespace, URIRef\n"
        "EX = Namespace('http://example.org/')\n"
        "OTHER = 42\n"
        "\n"
        "def build():\n"
        "    g = Graph()\n"
        "    g.add((EX.a, EX.p, EX.b))\n"
        "    g.add((EX.b, EX.p, EX.c))\n"
        "    return g\n"
        "\n"
        "def unrelated():\n"
        "    return OTHER\n"
    )
    regs = extract_regions(src, RCFG)
    assert len(regs) == 1
    reg = regs[0]
    assert reg["kind"] == "function"
    assert reg["qualname"] == "build"
    assert reg["rdf_ops"] >= 3
    ctx = "\n".join(reg["context"])
    assert "EX = Namespace" in ctx
    assert "from rdflib import" in ctx
    assert "OTHER" not in ctx           # not read by the region


def test_whole_file_when_ops_at_module_level():
    src = (
        "from rdflib import Graph, URIRef\n"
        "g = Graph()\n"
        "g.add((URIRef('http://a'), URIRef('http://b'), URIRef('http://c')))\n"
        "g.serialize()\n"
    )
    regs = extract_regions(src, RCFG)
    assert len(regs) == 1
    assert regs[0]["kind"] == "file"


def test_no_rdf_no_region():
    assert extract_regions("x = 1\n", RCFG) == []


def test_nested_function_innermost_only():
    src = (
        "from rdflib import Graph, URIRef\n"
        "def outer():\n"
        "    def inner():\n"
        "        g = Graph()\n"
        "        g.add((URIRef('http://a'), URIRef('http://b'), URIRef('http://c')))\n"
        "        return g\n"
        "    return inner()\n"
    )
    regs = extract_regions(src, RCFG)
    quals = [r["qualname"] for r in regs]
    assert quals == ["outer.inner"]


def test_band_assignment():
    cfg = {"band_low": [0.0, 0.05], "band_medium": [0.05, 0.20],
           "band_high": [0.20, 1.0]}
    assert band_of(0.0, cfg) == "low"
    assert band_of(0.04999, cfg) == "low"
    assert band_of(0.05, cfg) == "medium"
    assert band_of(0.35, cfg) == "high"
    assert band_of(1.0, cfg) == "high"

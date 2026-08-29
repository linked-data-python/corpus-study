"""Tests of region extraction.

The wave-drawing and density-band tests that used to live here went
with `rdfeval/sample.py` when the two studies collapsed into one
(2026-08-29): the draw is stratified by kind of use now, and its own
tests are in `test_strata.py`. Region extraction survived both draws
— `rdfeval.strata` calls it for every site — so its tests stay.
"""

from rdfeval.regions import extract_regions

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


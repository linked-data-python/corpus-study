# Context shim (see meta.json): T (a taxonomy module), HERE, SP and byid --
# restored from altunelyusuf/SemanticTechnologies@bad0fa7c46
# landscape/07-tooling/build_page_v6_4_0.py, lines 9-11 and 22-40 -- defined
# earlier in the same source file, just outside this region's extracted
# line range (90-97). Values copied verbatim from the real repository:
#   - T.BASE, from landscape/07-tooling/taxonomy_v1_0_0.py line 11
#     (BASE = "http://example.org/semtech#");
#   - SP, from build_page_v6_4_0.py line 11
#     (SP = Namespace("http://example.org/semtech/page#"));
#   - byid["T1C3"]["refs"], from taxonomy_v1_0_0.py's TAX literal, the
#     T1C3 ("Query Languages") node's refs=["W3C-SPARQL11","R16","R14"]
#     (only "refs" is reproduced: it is the only key this region reads
#     off byid["T1C3"]);
#   - REG, the subset S() needs for this region -- "W3C-SPARQL11", "R16"
#     and "R14" copied verbatim from taxonomy_v1_0_0.py's C/_TC dicts,
#     "NR-PYODIDE" copied verbatim from enrichment_h_v4_0_0.py. The real
#     REG in the source module merges eight such registries loaded from
#     sibling files (tax.C, rx.EXT, ec.EXT2, eh.EXT4, ej.EXT5, el.EXT6,
#     em.EXT7, eo.EXT8); none of their other entries this region reads.
# HERE's real value ("/home/claude/semtech-landscape", the original
# author's own machine) is redirected to this shim's own landscape/
# subdirectory, which holds a minimal placeholder for
# semtech_page_abox_v6_3_0.ttl (see that file's own header: this region
# never reads the pre-existing graph, only adds to it).
# Identical for both representations.
import os
from types import SimpleNamespace
from rdflib import Namespace

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "landscape")

T = SimpleNamespace(BASE="http://example.org/semtech#")

SP = Namespace("http://example.org/semtech/page#")

byid = {
    "T1C3": {"refs": ["W3C-SPARQL11", "R16", "R14"]},
}

REG = {
    "W3C-SPARQL11": {
        "cite": "W3C (2013). SPARQL 1.1 Query Language. Recommendation.",
        "url": "https://www.w3.org/TR/sparql11-query/",
    },
    "R16": {
        "cite": "ISO/IEC (2024-04). ISO/IEC 39075:2024 Database languages - GQL, "
                "the first new ISO database language since SQL (1987); SQL/PGQ "
                "published 2023 as SQL Part 16.",
        "url": "https://www.iso.org/standard/76120.html",
    },
    "R14": {
        "cite": "W3C RDF & SPARQL Working Group (2025-2026). RDF 1.2 and SPARQL "
                "1.2 specification family (twelve Recommendation-track "
                "documents; RDF 1.2 Concepts at Candidate Recommendation; "
                "What's New in RDF 1.2 group note draft).",
        "url": "https://www.w3.org/TR/sparql12-query/",
    },
    "NR-PYODIDE": {
        "cite": "Pyodide project (2026). Pyodide documentation: the CPython "
                "scientific stack compiled to WebAssembly for in-browser "
                "execution.",
        "url": "https://pyodide.org/en/stable/",
    },
}


def S(*keys):
    return " | ".join(REG[k]["cite"] for k in keys)

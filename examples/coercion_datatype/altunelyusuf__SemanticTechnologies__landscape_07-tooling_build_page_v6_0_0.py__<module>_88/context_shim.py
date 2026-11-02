# Context shim (see meta.json): restores `HERE`, `S` and `byid`, used but not
# defined in the extracted region, from altunelyusuf/SemanticTechnologies
# @ bad0fa7c46af (landscape/07-tooling/build_page_v6_0_0.py, verified against
# the source repository at that commit).
#
# `S` is copied VERBATIM from build_page_v6_0_0.py:
#     def S(*keys): return " | ".join(REG[k]["cite"] for k in keys)
# There, `REG` merges nine registries loaded dynamically from a hardcoded
# local path (`HERE = "/home/claude/semtech-landscape"`) that does not exist
# here. Only the four keys the region looks up are reproduced, their "cite"
# copied verbatim from their real source: R14 and R16 (`C` in taxonomy_v1_0_0.py),
# W3C-SPARQL11 (`_TC` in the same file, whose first tuple item becomes the
# cite) and NR-PYODIDE (EXT4 in enrichment_h_v4_0_0.py).
#
# `byid` maps a taxonomy node id to its node; the region reads only
# byid["T1C3"]["refs"], whose value is copied from the node
# t("T1C3", "Query Languages", ...) of taxonomy_v1_0_0.py.
#
# `HERE` resolves to this shim's own directory, which holds a minimal
# stand-in 04-page/semtech_page_abox_v5_4_0.ttl (both sides parse the same
# file at the same path).
import os

HERE = os.path.dirname(os.path.abspath(__file__))

REG = {
    "R14": {"cite": "W3C RDF & SPARQL Working Group (2025-2026). RDF 1.2 and SPARQL 1.2 specification family (twelve Recommendation-track documents; RDF 1.2 Concepts at Candidate Recommendation; What's New in RDF 1.2 group note draft)."},
    "R16": {"cite": "ISO/IEC (2024-04). ISO/IEC 39075:2024 Database languages - GQL, the first new ISO database language since SQL (1987); SQL/PGQ published 2023 as SQL Part 16."},
    "W3C-SPARQL11": {"cite": "W3C (2013). SPARQL 1.1 Query Language. Recommendation."},
    "NR-PYODIDE": {"cite": "Pyodide project (2026). Pyodide documentation: the CPython scientific stack compiled to WebAssembly for in-browser execution."},
}

byid = {"T1C3": {"id": "T1C3", "refs": ["W3C-SPARQL11", "R16", "R14"]}}


def S(*keys): return " | ".join(REG[k]["cite"] for k in keys)

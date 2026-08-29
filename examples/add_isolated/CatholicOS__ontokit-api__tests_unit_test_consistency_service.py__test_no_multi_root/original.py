# Extracted from CatholicOS/ontokit-api@23680a4d04 : tests/unit/test_consistency_service.py
# region: test_no_multi_root (lines 226-233, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import OWL, RDF, RDFS
from ontokit.services.consistency_service import (
    _check_cycle_detect,
    _check_dangling_ref,
    _check_deprecated_parent,
    _check_duplicate_label,
    _check_missing_comment,
    _check_missing_label,
    _check_multi_root,
    _check_orphan_class,
    _check_unused_property,
    run_consistency_check,
)
EX = Namespace("http://example.org/")

def test_no_multi_root() -> None:
    g = Graph()
    # 5 root classes — at threshold, should NOT trigger
    for i in range(5):
        cls = EX[f"Root{i}"]
        g.add((cls, RDF.type, OWL.Class))
    issues = _check_multi_root(g)
    assert len(issues) == 0

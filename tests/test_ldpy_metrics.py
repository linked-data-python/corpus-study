"""Tests of the ldpy-side surface/structure metrics."""

import pytest

from rdfeval.ldpy_metrics import (
    LdpyMetricsError, count_triples, measure_ldpy_source)


def test_pure_python_has_no_islands():
    m = measure_ldpy_source("x = 1\ny = x + 2\n")
    assert m.islands == 0
    assert m.terms == 0
    assert m.triples_semantic == 0
    assert m.tokens > 0


def test_simple_graph():
    src = (
        "@prefix ex: <http://e/> .\n"
        "g = g{ ex:s a ex:C ; ex:p 1 }\n"
    )
    m = measure_ldpy_source(src)
    assert m.islands == 2                       # prefix decl + graph
    assert m.island_kinds.get("island:prefix") == 1
    assert m.island_kinds.get("island:graph") == 1
    assert m.triples_semantic == 2
    assert m.triples_expressed == 2
    # terms in the graph: ex:s, a, ex:C, ex:p, 1  (+ prefix decl's ex: and IRI)
    assert m.terms >= 5
    assert m.loc == 2
    assert m.code_loc == 2


def test_interpolation_counts_python_tokens():
    src = (
        "@prefix ex: <http://e/> .\n"
        "v = 21\n"
        "g = g{ ex:s ex:val {v + 1} }\n"
    )
    m = measure_ldpy_source(src)
    assert m.triples_semantic == 1
    # the interpolation is one term; its interior tokens are counted
    assert m.tokens > 10


def test_bnode_and_collection_expansion():
    src = (
        "@prefix ex: <http://e/> .\n"
        "v = 3\n"
        "g = g{ ex:s ex:r [ ex:value {v} ] ; ex:tags ( 1 2 ) }\n"
    )
    m = measure_ldpy_source(src)
    assert m.triples_semantic == 7              # incl. rdf:first/rest chain
    assert m.triples_expressed == 3             # notation-level assertions


def test_pname_and_iri_islands():
    src = (
        "@prefix ex: <http://e/> .\n"
        "u = ex:thing\n"
        "w = <http://e/other>\n"
    )
    m = measure_ldpy_source(src)
    assert m.island_kinds.get("island:pname") == 1
    assert m.island_kinds.get("island:iri") == 1
    assert m.triples_semantic == 0


def test_invalid_source_raises():
    with pytest.raises(LdpyMetricsError):
        measure_ldpy_source("def broken(:\n")


def test_count_triples_multi_statement():
    body = " ex:a ex:p 1 . ex:b ex:q 2, 3 "
    assert count_triples(body) == 3


def test_scaffolding_lower_than_python():
    """The headline claim, in miniature: fewer scaffolding tokens per triple
    in the island than in the equivalent rdflib calls."""
    src = (
        "@prefix ex: <http://e/> .\n"
        "g = g{ ex:s ex:p ex:o . ex:s ex:q ex:r }\n"
    )
    m = measure_ldpy_source(src)
    assert m.triples_expressed == 2
    per_triple = m.scaffolding_tokens / m.triples_expressed
    # rdflib needs >= 8 scaffolding tokens per g.add((...)) call
    assert per_triple < 8

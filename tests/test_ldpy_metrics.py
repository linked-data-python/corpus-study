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


# --- assertions and patterns are counted apart -------------------

MIXED = """\
@prefix ex: <http://example.org/> .
@graph as g
+{ ex:a a ex:C ; ex:p 1, 2 }
-{ ex:a ex:p ?o }
x = g{ ex:b ex:q 3 }
rows = m{ ?s a ex:C ; ex:p ?v }
"""


def test_the_statement_islands_assert_triples_too():
    """`+{ }` asserts exactly like `g{ }`.  Counting only `g{ }` left every
    per-triple ratio of the construction strata undefined."""
    from rdfeval.ldpy_metrics import measure_ldpy_source
    m = measure_ldpy_source(MIXED)
    assert m.triples_expressed == 4       # 3 in +{ }, 1 in g{ }
    assert m.triples_semantic == 4


def test_patterns_are_not_pooled_with_triples():
    """A pattern with a wildcard is not a triple: pooling the two would
    corrupt every per-triple ratio."""
    from rdfeval.ldpy_metrics import measure_ldpy_source
    m = measure_ldpy_source(MIXED)
    assert m.patterns_expressed == 3      # 1 in -{ }, 2 in m{ }
    assert m.patterns_semantic == 3


def test_a_reading_region_has_a_pattern_denominator():
    """`corr_*_per_triple` is undefined for a region that asserts nothing;
    it is the pattern count that gives it a unit."""
    from rdfeval.compare import measure_pair
    py = ("from rdflib import Graph, Namespace\n"
          "EX = Namespace('http://example.org/')\n"
          "g = Graph()\n"
          "xs = list(g.objects(EX.a, EX.p))\n"
          "y = g.value(EX.a, EX.q)\n")
    ld = ("@prefix ex: <http://example.org/> .\n"
          "@graph as g\n"
          "xs = list(m{ ex:a ex:p ?o })\n"
          "y = m{ ex:a ex:q ?v }.first()\n")
    r = measure_pair(py, ld)
    assert r["ldpy"]["triples_expressed"] == 0
    assert r["ldpy"]["corr_scaffolding_tokens_per_triple"] is None
    assert r["ldpy"]["patterns_expressed"] == 2
    assert r["ldpy"]["corr_scaffolding_tokens_per_pattern"] is not None
    assert r["python"]["patterns_read"] == 2
    assert r["python"]["triples_added"] == 0


def test_a_global_prefix_declaration_is_masked_with_its_modifier():
    """`global @prefix ex: <IRI> as EX .` is one statement.

    The language map leaves `global` to Python — it IS a Python keyword —
    so masking only the island left `global pass`, which does not parse, and
    the region silently lost every metric. The corpus has one function that
    declares nineteen prefixes this way.
    """
    from rdfeval.ldpy_metrics import measure_ldpy_source
    m = measure_ldpy_source(
        "def f():\n"
        "    global @prefix ex: <http://e/> as EX .\n"
        "    global @base <http://e/> .\n"
        "    return EX\n")
    assert "global pass" not in m.masked_source
    assert m.islands == 2
    assert m.syntax_nodes > 0

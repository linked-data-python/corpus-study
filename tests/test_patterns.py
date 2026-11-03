"""Validation by translation patterns (rdfeval.patterns, record corpus/403)."""

from rdfeval import patterns as P

ORIG = '''from rdflib import Graph, Namespace, RDF
EX = Namespace("http://example.org/")


def build(g, s, name):
    g.add((s, RDF.type, EX.Person))
    g.add((s, EX.name, name))
    return g.value(s, EX.name)
'''

TRANSLATED = '''from rdflib import Graph, Namespace, RDF
@prefix ex: <http://example.org/> .


def build(g, s, name):
    +{ {s} a ex:Person ; ex:name {name} }(g)
    return m{ {s} ex:name ?o }(g).first()
'''


def _rewrites():
    rws = P.rewrites("r", ORIG, TRANSLATED)
    for rw in rws:
        rw.rules = P.rules_of(rw, ORIG)
    return {rw.kind: rw for rw in rws}


def test_each_island_comes_with_the_python_it_replaces():
    rws = _rewrites()
    assert set(rws) >= {"prefix", "addto", "match"}
    assert "g.add((s, RDF.type, EX.Person))" in rws["addto"].python
    assert "g.value(s, EX.name)" in rws["match"].python


def test_statement_and_term_rules():
    rws = _rewrites()
    assert rws["prefix"].rules == ["@prefix ← Namespace()"]
    add = rws["addto"].rules
    assert add[0] == "+{ } ← .add()"
    assert {"term: a ← RDF.type", "term: p:l ← NS.l", "term: {x} ← x",
            "term: ; ← repeated subject", "(g) ← receiver"} <= set(add)
    assert rws["match"].rules[0] == "m{ }·first ← .value()"


def test_consumption_reads_the_line_around_the_island():
    assert P.consumption("x =", ".first()") == "first"
    assert P.consumption("if bool(", "):") == "bool"
    assert P.consumption("for o in", ":") == "for"
    assert P.consumption("assert", "") == "truth"
    assert P.consumption("rows = list(", ")") == "collect"
    assert P.consumption("x =", "") == "value"


def test_residual_names_a_restructuring_not_an_import():
    assert P.residual(ORIG, TRANSLATED) == []
    helper = TRANSLATED.replace("    return m{",
                                "    _TABLE = {}\n    return m{")
    assert P.residual(ORIG, helper) == ["_TABLE"]
    imported = "from rdflib import URIRef\n" + TRANSLATED
    assert P.residual(ORIG, imported) == []


def _pair(rid, rules, **kw):
    rw = P.Rewrite(rid, "addto", 1, "+{ }", "", "", "g.add(t)", "+{ }",
                   rules)
    return {"region_id": rid, "validation": "equivalent",
            "classification": "directly-expressible", "residual": [],
            "rewrites": [rw], **kw}


def test_coverage_needs_every_rule_approved_and_the_machine_checks():
    pairs = [_pair("a", ["r1", "r2"]), _pair("b", ["r1"]),
             _pair("c", ["r1"], classification="awkward"),
             _pair("d", ["r1"], residual=["helper"])]
    bound = P.coverage(pairs, None)
    assert bound["a"] == [] and bound["b"] == []
    assert bound["c"] == ["classification: awkward"]
    assert bound["d"][0].startswith("restructuring")
    now = P.coverage(pairs, {"r1"})
    assert now["b"] == []
    assert now["a"] == ["rules not approved: r2"]


def test_the_audit_draw_is_reproducible():
    covered = [f"r{i}" for i in range(50)]
    assert P.audit_draw(covered) == P.audit_draw(list(reversed(covered)))
    assert len(P.audit_draw(covered)) == P.AUDIT_SIZE
    assert P.audit_draw(["x"]) == ["x"]


def test_an_escaped_local_name_is_found_in_the_original():
    assert P._pname_rule("fhir:Coding\\.system", "v = FHIR.Coding.system") \
        == "term: p:l ← NS.l"

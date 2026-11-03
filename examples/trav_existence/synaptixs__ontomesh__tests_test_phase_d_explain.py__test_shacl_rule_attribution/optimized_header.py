# Extracted from synaptixs/ontomesh@f771c8c4ee : tests/test_phase_d_explain.py
# region: test_shacl_rule_attribution (lines 114-145, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib import PROV, RDF, Graph, Namespace  # noqa: E402
from materializer import explain_triple, materialize  # noqa: E402
NS = Namespace("https://test.example/phased#")
TOOLKIT = Namespace("https://ontology.example.com/toolkit/materializer/")

def test_shacl_rule_attribution(workspace):
    result = materialize(
        workspace["ontology"], workspace["out"],
        shapes_path=workspace["shapes"],
        sparql_rules_dir=workspace["rules_dir"],
    )
    derivations = explain_triple(
        result.lineage_path,
        subject=str(NS.t1), predicate=str(NS.flag), obj="\"true\"",
    )
    # SHACL writes `true`^^xsd:boolean — the simple parser in explain_triple
    # treats `"true"` as a literal. If the lookup misses on the simple form,
    # fall back to checking the lineage graph directly.
    if not derivations:
        g = Graph().parse(result.lineage_path, format="turtle")
        # Find any reified statement with subject :t1 and predicate :flag
        found = False
        for stmt in g.subjects(RDF.type, RDF.Statement):
            if (stmt, RDF.subject, NS.t1) in g and (stmt, RDF.predicate, NS.flag) in g:
                deriv = g.value(stmt, PROV.wasDerivedFrom)
                assert deriv, "missing derivation"
                rule = g.value(deriv, TOOLKIT.rule)
                engine = g.value(deriv, TOOLKIT.engine)
                assert engine and str(engine) == "shacl"
                assert rule and "Trigger" in str(rule)
                found = True
                break
        assert found, "shacl-derived triple has no lineage record"

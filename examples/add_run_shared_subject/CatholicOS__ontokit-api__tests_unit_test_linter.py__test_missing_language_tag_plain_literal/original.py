# Extracted from CatholicOS/ontokit-api@23680a4d04 : tests/unit/test_linter.py
# region: test_missing_language_tag_plain_literal (lines 555-567, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from uuid import uuid4
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS, SKOS, XSD
from ontokit.services.linter import (
    LINT_RULES,
    LintResult,
    OntologyLinter,
    get_available_rules,
    get_linter,
)
EX = Namespace("http://example.org/")
PROJECT_ID = uuid4()

async def test_missing_language_tag_plain_literal() -> None:
    """A plain literal without a language tag triggers missing-language-tag."""
    g = Graph()
    g.add((EX.Animal, RDF.type, OWL.Class))
    g.add((EX.Animal, RDFS.label, Literal("Animal")))  # no lang

    linter = OntologyLinter(enabled_rules={"missing-language-tag"})
    issues = await linter.lint(g, PROJECT_ID)

    matches = _results_with_rule(issues, "missing-language-tag")
    assert len(matches) == 1
    assert matches[0].issue_type == "warning"
    assert matches[0].subject_iri == str(EX.Animal)

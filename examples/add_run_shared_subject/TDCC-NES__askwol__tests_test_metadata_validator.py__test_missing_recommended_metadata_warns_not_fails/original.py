# Extracted from TDCC-NES/askwol@3534557e8b : tests/test_metadata_validator.py
# region: test_missing_recommended_metadata_warns_not_fails (lines 49-61, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import DC, DCTERMS, OWL, RDF, XSD
from askwol.metadata_validator import validate_ontology_metadata
from askwol.models import MetadataCheck, MetadataReport, Status, ValidationReport
EX = Namespace("https://example.org/ont/")

def test_missing_recommended_metadata_warns_not_fails():
    g = _base_graph()
    ont = EX[""]
    g.add((ont, DCTERMS.title, Literal("Example Ontology", lang="en")))
    g.add((ont, DCTERMS.description, Literal("An example ontology", lang="en")))
    g.add((ont, DCTERMS.creator, Literal("Example Team")))
    g.add((ont, DCTERMS.license, EX["license"]))
    g.add((ont, OWL.versionInfo, Literal("1.0")))

    report = validate_ontology_metadata(g)

    assert any(c.key == "created" and c.status == Status.WARN for c in report.checks)
    assert any(c.key == "publisher" and c.status == Status.WARN for c in report.checks)

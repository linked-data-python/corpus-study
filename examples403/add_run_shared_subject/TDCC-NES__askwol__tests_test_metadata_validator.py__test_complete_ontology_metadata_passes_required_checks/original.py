# Extracted from TDCC-NES/askwol@3534557e8b : tests/test_metadata_validator.py
# region: test_complete_ontology_metadata_passes_required_checks (lines 20-36, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import DC, DCTERMS, OWL, RDF, XSD
from askwol.metadata_validator import validate_ontology_metadata
from askwol.models import MetadataCheck, MetadataReport, Status, ValidationReport
EX = Namespace("https://example.org/ont/")

def test_complete_ontology_metadata_passes_required_checks():
    g = _base_graph()
    ont = EX[""]
    g.add((ont, DCTERMS.title, Literal("Example Ontology", lang="en")))
    g.add((ont, DCTERMS.description, Literal("An example ontology", lang="en")))
    g.add((ont, DCTERMS.creator, Literal("Example Team")))
    g.add((ont, DCTERMS.license, EX["license"]))
    g.add((ont, OWL.versionInfo, Literal("1.0")))
    g.add((ont, DCTERMS.created, Literal("2026-04-20", datatype=XSD.date)))
    g.add((ont, DCTERMS.publisher, Literal("TDCC-NES")))

    report = validate_ontology_metadata(g)

    assert report is not None
    assert report.failed_checks == 0
    assert report.passed_checks >= 5
    assert any(c.key == "title" and c.status == Status.OK for c in report.checks)

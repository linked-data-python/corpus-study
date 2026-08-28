# Extracted from Haigutus/triplets@7cf62970e8 : tests/test_shacl_report.py
# region: test_report_metadata (lines 103-118, stratum ns_def_local)
# licence of the source repository: see meta.json
from pathlib import Path
from triplets.validation.shacl_report import report_to_violations, violations_to_report_graph
VIOLATIONS = pandas.DataFrame([
    ("11111111-2222-3333-4444-555555555555", "Conductor.length", "100",
     "sh:maxInclusive", "too long", "Warning", "n0f320cdb3"),
    ("22222222-2222-3333-4444-555555555555", "IdentifiedObject.name", None,
     "sh:minCount", "needs a name", "Violation", "http://example.org/shapes#NameShape"),
    ("33333333-2222-3333-4444-555555555555", "ACLineSegment.r", "0.66",
     "sh:sparql", "R/X ratio high", "Violation", "n0f320cdb3"),
    ("44444444-2222-3333-4444-555555555555", "Conductor.length", "1",
     "triplets:lexicalForm", "integer form for a float", "Warning", None),
], columns=VIOLATION_COLUMNS)

def test_report_metadata():
    import rdflib
    from triplets.validation.shacl_report import violations_to_report_graph

    prov = rdflib.Namespace("http://www.w3.org/ns/prov#")
    dcterms = rdflib.Namespace("http://purl.org/dc/terms/")
    sh = rdflib.Namespace("http://www.w3.org/ns/shacl#")

    graph = violations_to_report_graph(
        VIOLATIONS, report_source="file.xml", report_references=[Path("a.ttl"), "b.ttl"])
    report = next(graph.subjects(rdflib.RDF.type, sh.ValidationReport))

    assert graph.value(report, prov.generatedAtTime) is not None
    assert "triplets" in str(graph.value(report, dcterms.creator))
    assert {str(v) for v in graph.objects(report, dcterms.source)} == {"file.xml"}
    assert {str(v) for v in graph.objects(report, dcterms.references)} == {"a.ttl", "b.ttl"}

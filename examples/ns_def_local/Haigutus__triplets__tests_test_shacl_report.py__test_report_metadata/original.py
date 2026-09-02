# Extracted from Haigutus/triplets@7cf62970e8 : tests/test_shacl_report.py
# region: test_report_metadata (lines 103-118, stratum ns_def_local)
# licence of the source repository: see meta.json
from pathlib import Path
import pandas
from triplets.validation.shacl_report import (
    VIOLATION_COLUMNS,
    report_to_violations,
    violations_to_report_graph,
)
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

    has_generated_at = graph.value(report, prov.generatedAtTime) is not None
    creator = str(graph.value(report, dcterms.creator))
    sources = {str(v) for v in graph.objects(report, dcterms.source)}
    references = {str(v) for v in graph.objects(report, dcterms.references)}

    assert has_generated_at
    assert "triplets" in creator
    assert sources == {"file.xml"}
    assert references == {"a.ttl", "b.ttl"}

    # Test harness only (see meta.json): the original test only asserts and
    # returns None, but comparing None tells the driver nothing.  The actual
    # generatedAtTime value is non-deterministic (wall-clock), so it cannot
    # be returned as-is; returning the same four values the assertions
    # already check (whether it is present, plus the deterministic ones
    # verbatim) gives the driver something comparable without inventing any
    # new check.
    return has_generated_at, "triplets" in creator, sources, references

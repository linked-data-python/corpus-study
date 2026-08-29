# Extracted from aigora-de/rdf-construct@670e400ea4 : src/rdf_construct/puml2rdf/validators.py
# region: RdfValidator._check_property_completeness (lines 355-400, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, RDF, RDFS
from rdflib.namespace import OWL

def _check_property_completeness(self, graph: Graph) -> list[ValidationIssue]:
    """Check that properties have domain and range."""
    issues = []

    for prop in graph.subjects(RDF.type, OWL.ObjectProperty):
        if not isinstance(prop, URIRef):
            continue

        has_domain = any(graph.objects(prop, RDFS.domain))
        has_range = any(graph.objects(prop, RDFS.range))

        if not has_domain:
            issues.append(
                ValidationIssue(
                    severity=Severity.INFO,
                    code="MISSING_DOMAIN",
                    message="Object property has no domain",
                    entity=str(prop),
                )
            )
        if not has_range:
            issues.append(
                ValidationIssue(
                    severity=Severity.INFO,
                    code="MISSING_RANGE",
                    message="Object property has no range",
                    entity=str(prop),
                )
            )

    for prop in graph.subjects(RDF.type, OWL.DatatypeProperty):
        if not isinstance(prop, URIRef):
            continue

        has_range = any(graph.objects(prop, RDFS.range))
        if not has_range:
            issues.append(
                ValidationIssue(
                    severity=Severity.INFO,
                    code="MISSING_RANGE",
                    message="Datatype property has no range (XSD type)",
                    entity=str(prop),
                )
            )

    return issues

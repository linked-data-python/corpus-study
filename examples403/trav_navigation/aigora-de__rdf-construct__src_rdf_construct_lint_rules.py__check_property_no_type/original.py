# Extracted from aigora-de/rdf-construct@670e400ea4 : src/rdf_construct/lint/rules.py
# region: check_property_no_type (lines 356-406, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import OWL

@lint_rule(
    rule_id="property-no-type",
    description="Property lacks explicit rdf:type declaration",
    category="structural",
    default_severity=Severity.ERROR,
)
def check_property_no_type(graph: Graph) -> list[LintIssue]:
    """Check for properties without explicit type.

    This catches subjects that have domain/range but no property type.
    """
    issues = []

    # Find all subjects that have domain or range but no property type
    property_types = {
        RDF.Property,
        OWL.ObjectProperty,
        OWL.DatatypeProperty,
        OWL.AnnotationProperty,
    }

    for subj in graph.subjects(RDFS.domain, None):
        if isinstance(subj, URIRef) and not is_builtin(subj):
            types = set(graph.objects(subj, RDF.type))
            if not types.intersection(property_types):
                issues.append(
                    LintIssue(
                        rule_id="property-no-type",
                        severity=Severity.ERROR,
                        entity=subj,
                        message="Has rdfs:domain but no property type declaration",
                    )
                )

    for subj in graph.subjects(RDFS.range, None):
        if isinstance(subj, URIRef) and not is_builtin(subj):
            types = set(graph.objects(subj, RDF.type))
            if not types.intersection(property_types):
                # Avoid duplicates if already reported
                existing = [i for i in issues if i.entity == subj]
                if not existing:
                    issues.append(
                        LintIssue(
                            rule_id="property-no-type",
                            severity=Severity.ERROR,
                            entity=subj,
                            message="Has rdfs:range but no property type declaration",
                        )
                    )

    return issues

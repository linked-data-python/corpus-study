# Extracted from aigora-de/rdf-construct@670e400ea4 : src/rdf_construct/lint/rules.py
# region: check_property_no_type (lines 356-406, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import OWL
from context_shim import LintIssue, Severity, is_builtin, lint_rule  # context shim -- see meta.json

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
    property_types = {RDF.Property, OWL.ObjectProperty,
                      OWL.DatatypeProperty, OWL.AnnotationProperty}

    for predicate, name in ((RDFS.domain, "rdfs:domain"), (RDFS.range, "rdfs:range")):
        for subj in graph.subjects(predicate, None):
            if (isinstance(subj, URIRef) and not is_builtin(subj)
                    and property_types.isdisjoint(graph.objects(subj, RDF.type))
                    # Avoid duplicates if already reported
                    and (predicate == RDFS.domain or not any(i.entity == subj for i in issues))):
                issues.append(LintIssue(
                    rule_id="property-no-type", severity=Severity.ERROR, entity=subj,
                    message=f"Has {name} but no property type declaration"))

    return issues

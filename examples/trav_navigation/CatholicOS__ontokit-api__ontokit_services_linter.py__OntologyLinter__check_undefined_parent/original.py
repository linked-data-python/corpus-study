# Extracted from CatholicOS/ontokit-api@23680a4d04 : ontokit/services/linter.py
# region: OntologyLinter._check_undefined_parent (lines 395-434, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS, SKOS, XSD
from ontokit.models.lint import LintIssueType

async def _check_undefined_parent(self, graph: Graph) -> list[LintResult]:
    """Find classes that reference undefined parent classes."""
    issues = []

    # Build set of all defined classes
    defined_classes = {
        str(c) for c in graph.subjects(RDF.type, OWL.Class) if isinstance(c, URIRef)
    }
    # Add owl:Thing as it's always implicitly defined
    defined_classes.add(str(OWL.Thing))

    for class_uri in graph.subjects(RDF.type, OWL.Class):
        if not isinstance(class_uri, URIRef):
            continue

        # Check each parent
        for parent_uri in graph.objects(class_uri, RDFS.subClassOf):
            if not isinstance(parent_uri, URIRef):
                continue

            parent_str = str(parent_uri)
            if parent_str not in defined_classes:
                label = self._get_label(graph, class_uri)
                issues.append(
                    LintResult(
                        issue_type=LintIssueType.ERROR.value,
                        rule_id="undefined-parent",
                        message="References undefined parent class",
                        subject_iri=str(class_uri),
                        subject_type="class",
                        details={
                            "local_name": self._get_local_name(class_uri),
                            "label": label,
                            "undefined_parent": parent_str,
                            "undefined_parent_local": self._get_local_name(parent_uri),
                        },
                    )
                )

    return issues

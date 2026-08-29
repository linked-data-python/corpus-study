# Extracted from CatholicOS/ontokit-api@23680a4d04 : ontokit/services/linter.py
# region: OntologyLinter._check_orphan_class (lines 354-393, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS, SKOS, XSD
from context_shim import LintIssueType, LintResult, OntologyLinter  # context shim -- see meta.json

async def _check_orphan_class(self, graph: Graph) -> list[LintResult]:
    """Find classes with no parent (other than owl:Thing) and no children."""
    issues = []

    owl_thing = OWL.Thing

    for class_uri in graph.subjects(RDF.type, OWL.Class):
        if not isinstance(class_uri, URIRef):
            continue
        if class_uri == owl_thing:
            continue

        # Get parents (excluding owl:Thing)
        parents = [
            p
            for p in graph.objects(class_uri, RDFS.subClassOf)
            if isinstance(p, URIRef) and p != owl_thing
        ]

        # Get children
        children = list(graph.subjects(RDFS.subClassOf, class_uri))

        # Orphan if no meaningful parents and no children
        if not parents and not children:
            label = self._get_label(graph, class_uri)
            issues.append(
                LintResult(
                    issue_type=LintIssueType.WARNING.value,
                    rule_id="orphan-class",
                    message="Class has no parent classes and no children",
                    subject_iri=str(class_uri),
                    subject_type="class",
                    details={
                        "local_name": self._get_local_name(class_uri),
                        "label": label,
                    },
                )
            )

    return issues


# Test harness only (see meta.json): `run_pair` calls its entry point
# synchronously, with no event loop, and `_check_orphan_class` is `async def`
# in its home class (there is no `await` anywhere in the region's own 40
# lines -- it is declared async only for consistency with its sibling
# `_check_*` methods, which the OntologyLinter.lint() orchestrator awaits).
# This wrapper drives the coroutine to completion; the region above is
# untouched.
import asyncio


def run_check_orphan_class(self, graph):
    return asyncio.run(_check_orphan_class(self, graph))

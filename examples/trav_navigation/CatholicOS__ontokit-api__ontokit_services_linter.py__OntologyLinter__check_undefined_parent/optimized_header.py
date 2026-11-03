# Extracted from CatholicOS/ontokit-api@23680a4d04 : ontokit/services/linter.py
# region: OntologyLinter._check_undefined_parent (lines 395-434, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef
from rdflib.namespace import OWL, RDF, RDFS
from context_shim import LintIssueType, LintResult  # context shim -- see meta.json

async def _check_undefined_parent(self, graph: Graph) -> list[LintResult]:
    """Find classes that reference undefined parent classes."""
    # Build set of all defined classes
    # Add owl:Thing as it's always implicitly defined
    defined_classes = {
        str(c) for c in graph.subjects(RDF.type, OWL.Class) if isinstance(c, URIRef)
    } | {str(OWL.Thing)}

    return [
        LintResult(
            issue_type=LintIssueType.ERROR.value,
            rule_id="undefined-parent",
            message="References undefined parent class",
            subject_iri=str(class_uri),
            subject_type="class",
            details={
                "local_name": self._get_local_name(class_uri),
                "label": self._get_label(graph, class_uri),
                "undefined_parent": str(parent_uri),
                "undefined_parent_local": self._get_local_name(parent_uri),
            },
        )
        for class_uri in graph.subjects(RDF.type, OWL.Class)
        if isinstance(class_uri, URIRef)
        # Check each parent
        for parent_uri in graph.objects(class_uri, RDFS.subClassOf)
        if isinstance(parent_uri, URIRef) and str(parent_uri) not in defined_classes
    ]


# Test harness only (see meta.json): `run_pair` calls its entry point
# synchronously, with no event loop, and `_check_undefined_parent` is
# `async def` in its home class (there is no `await` anywhere in the
# region's own 40 lines -- it is declared async only for consistency with
# its sibling `_check_*` methods, which the OntologyLinter.lint() orchestrator
# awaits). This wrapper drives the coroutine to completion; the region above
# is untouched.
import asyncio


def run_check_undefined_parent(self, graph):
    return asyncio.run(_check_undefined_parent(self, graph))

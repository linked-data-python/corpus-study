# Context shim (see meta.json): subset of ontokit/services/linter.py and
# ontokit/models/lint.py from CatholicOS/ontokit-api@23680a4d0453f5951716d0
# 45a4d05bd5396d22a4, so the region executes outside its package. Identical
# bindings for both representations.
#
# LintResult is the dataclass the region builds and returns, copied verbatim.
# LintIssueType is the severity enum the region reads (LintIssueType.WARNING),
# copied verbatim (as a plain Enum here -- the real one is a StrEnum backed by
# a SQLAlchemy-facing model module the region never touches; `.value` behaves
# identically either way).
#
# OntologyLinter stands in for the real class only as the `self` receiver
# `_check_orphan_class` needs: its two @staticmethod helpers, reproduced
# verbatim (they have no other state, so a single shared instance is reused
# as `self` on both sides of every call -- see driver.py). The real class is
# a @dataclass carrying an `enabled_rules` field and a `lint()` orchestrator
# the region never calls; neither is needed here.
from dataclasses import dataclass
from enum import Enum
from typing import Any

from rdflib import Graph, RDFS, URIRef
from rdflib import Literal as RDFLiteral


class LintIssueType(Enum):
    """Severity levels for lint issues."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class LintResult:
    """Result from a lint check."""

    issue_type: str  # error, warning, info
    rule_id: str
    message: str
    subject_iri: str | None = None
    subject_type: str | None = None  # "class", "property", "individual", "other"
    details: dict[str, Any] | None = None


class OntologyLinter:
    """Stand-in receiver: only the two static helpers the region calls on `self`."""

    @staticmethod
    def _get_local_name(uri: URIRef) -> str:
        """Extract local name from IRI (after # or last /)."""
        iri = str(uri)
        if "#" in iri:
            return iri.split("#")[-1]
        return iri.rsplit("/", 1)[-1]

    @staticmethod
    def _get_label(graph: Graph, uri: URIRef) -> str | None:
        """Get the first rdfs:label for a URI."""
        for label in graph.objects(uri, RDFS.label):
            if isinstance(label, RDFLiteral):
                return str(label)
        return None

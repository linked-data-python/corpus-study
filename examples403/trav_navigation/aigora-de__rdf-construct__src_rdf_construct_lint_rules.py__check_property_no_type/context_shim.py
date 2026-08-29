# Context shim (see meta.json): subset of src/rdf_construct/lint/rules.py
# from aigora-de/rdf-construct@670e400ea43804775652dc94751a85e33e04ba23, so
# the region executes outside its package. Identical bindings for both
# representations.
#
# Severity, LintIssue, RuleSpec, the `lint_rule` registration decorator and
# `is_builtin` are copied verbatim; `_RULE_REGISTRY` is the same
# module-level dict the decorator populates in the real file (the region
# never reads it back, but the decorator still needs somewhere to register
# into).
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable

from rdflib import Graph, URIRef


class Severity(Enum):
    """Severity levels for lint issues."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

    def __lt__(self, other: Severity) -> bool:
        order = {Severity.INFO: 0, Severity.WARNING: 1, Severity.ERROR: 2}
        return order[self] < order[other]


@dataclass
class LintIssue:
    """A single lint issue found in an ontology."""

    rule_id: str
    severity: Severity
    entity: URIRef | None
    message: str
    line: int | None = None

    def __str__(self) -> str:
        entity_str = f" '{self.entity}'" if self.entity else ""
        line_str = f":{self.line}" if self.line else ""
        return f"{line_str} {self.severity.value}[{self.rule_id}]:{entity_str} {self.message}"


@dataclass
class RuleSpec:
    """Specification for a lint rule."""

    rule_id: str
    description: str
    category: str
    default_severity: Severity
    check_fn: Callable[[Graph], list[LintIssue]]


_RULE_REGISTRY: dict[str, RuleSpec] = {}


def lint_rule(
    rule_id: str,
    description: str,
    category: str,
    default_severity: Severity,
) -> Callable:
    """Decorator to register a lint rule."""

    def decorator(fn: Callable[[Graph], list[LintIssue]]) -> Callable:
        spec = RuleSpec(
            rule_id=rule_id,
            description=description,
            category=category,
            default_severity=default_severity,
            check_fn=fn,
        )
        _RULE_REGISTRY[rule_id] = spec
        return fn

    return decorator


def is_builtin(uri: URIRef) -> bool:
    """Check if a URI is from a built-in namespace (RDF, RDFS, OWL, XSD)."""
    builtin_namespaces = [
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "http://www.w3.org/2000/01/rdf-schema#",
        "http://www.w3.org/2002/07/owl#",
        "http://www.w3.org/2001/XMLSchema#",
    ]
    uri_str = str(uri)
    return any(uri_str.startswith(ns) for ns in builtin_namespaces)

# Extracted from zwelz3/holonic@d8d1758752 : src/holonic/client.py
# region: _parse_shacl_report (lines 285-345, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Dataset, Graph, Literal, Namespace, URIRef
from holonic.model import (
    AuditTrail,
    HolonInfo,
    MembraneHealth,
    MembraneResult,
    PortalInfo,
    ShapeViolation,
    SurfaceReport,
    TraversalRecord,
    ValidationRecord,
)
SH = Namespace("http://www.w3.org/ns/shacl#")

def _parse_shacl_report(
    report_graph: Graph,
) -> tuple[list[str], list[str], list[ShapeViolation]]:
    """Extract violations and warnings from a SHACL validation report graph.

    Parses the structured ``sh:ValidationResult`` entries rather than
    scanning the human-readable text, making the result independent
    of pyshacl's text-formatting choices.

    Returns ``(violations, warnings, shape_violations)`` where
    ``violations`` and ``warnings`` are human-readable summary strings,
    and ``shape_violations`` is a list of structured
    :class:`ShapeViolation` objects.
    """
    violations: list[str] = []
    warnings: list[str] = []
    structured: list[ShapeViolation] = []

    for result in report_graph.objects(predicate=SH.result):
        severity = report_graph.value(result, SH.resultSeverity)
        message = report_graph.value(result, SH.resultMessage)
        focus = report_graph.value(result, SH.focusNode)
        path = report_graph.value(result, SH.resultPath)
        source_shape = report_graph.value(result, SH.sourceShape)
        value = report_graph.value(result, SH.value)

        severity_str = str(severity) if severity else ""
        msg = str(message) if message else "No message"
        focus_str = str(focus) if focus else ""
        path_str = str(path) if path else ""

        detail_parts = [msg]
        if focus_str:
            detail_parts.append(f"focus={focus_str}")
        if path_str:
            detail_parts.append(f"path={path_str}")
        detail = "; ".join(detail_parts)

        sev_label = "Violation"
        if severity_str.endswith("Violation"):
            violations.append(f"Violation: {detail}")
            sev_label = "Violation"
        elif severity_str.endswith("Warning"):
            warnings.append(f"Warning: {detail}")
            sev_label = "Warning"
        else:
            # Info severity: skip for violation/warning lists
            continue

        structured.append(
            ShapeViolation(
                shape_iri=str(source_shape) if source_shape else None,
                focus_node=focus_str or None,
                path=path_str or None,
                value=str(value) if value else None,
                message=msg,
                severity=sev_label,
            )
        )

    return violations, warnings, structured

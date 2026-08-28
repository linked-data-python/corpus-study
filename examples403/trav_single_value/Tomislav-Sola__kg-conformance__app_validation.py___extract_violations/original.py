# Extracted from Tomislav-Sola/kg-conformance@964fd4ad4e : app/validation.py
# region: _extract_violations (lines 53-65, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, RDF
SH = Namespace("http://www.w3.org/ns/shacl#")
_RESULT_FIELDS: tuple[tuple[str, object], ...] = (
    ("focus_node", SH.focusNode),
    ("path", SH.resultPath),
    ("source_shape", SH.sourceShape),
    ("constraint_component", SH.sourceConstraintComponent),
    ("severity", SH.resultSeverity),
    ("message", SH.resultMessage),
)

def _extract_violations(results_graph: Graph) -> list[dict]:
    """Translate the SHACL results graph into a list of violation dicts."""

    violations: list[dict] = []
    for result in results_graph.subjects(RDF.type, SH.ValidationResult):
        violation = {}
        for key, predicate in _RESULT_FIELDS:
            value = results_graph.value(result, predicate)
            violation[key] = str(value) if value is not None else None
        violations.append(violation)

    violations.sort(key=lambda v: tuple(v[key] or "" for key, _ in _RESULT_FIELDS))
    return violations

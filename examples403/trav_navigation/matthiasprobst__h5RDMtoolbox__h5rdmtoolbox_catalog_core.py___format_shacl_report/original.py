# Extracted from matthiasprobst/h5RDMtoolbox@1baa9284dc : h5rdmtoolbox/catalog/core.py
# region: _format_shacl_report (lines 945-966, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace
from rdflib.namespace import RDF
SH = Namespace("http://www.w3.org/ns/shacl#")

def _format_shacl_report(turtle_text: str) -> str:
    g = Graph()
    g.parse(data=turtle_text, format="turtle")

    messages = []

    for result in g.subjects(RDF.type, SH.ValidationResult):
        focus = g.value(result, SH.focusNode)
        path = g.value(result, SH.resultPath)
        value = g.value(result, SH.value)
        severity = g.value(result, SH.resultSeverity)
        component = g.value(result, SH.sourceConstraintComponent)

        messages.append(
            f"- Resource: {focus}\n"
            f"  Property: {path}\n"
            f"  Invalid value: {value}\n"
            f"  Constraint: {component.split('#')[-1] if component else 'Unknown'}\n"
            f"  Severity: {severity.split('#')[-1] if severity else 'Unknown'}"
        )

    return "\n\n".join(messages) if messages else "No SHACL violations found."

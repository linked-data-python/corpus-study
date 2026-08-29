# Extracted from MaxBerktoldRWTH/BRICKbuilder@28f0710933 : src/validation/shacl.py
# region: ShaclValidationResult._extract_violations (lines 16-40, stratum trav_navigation)
# licence of the source repository: see meta.json
import rdflib
SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")

def _extract_violations(self):
    """
    Extract validation result rows from the SHACL report graph.
    Returns a list of dictionaries for display in the GUI.
    """
    violations = []

    for result in self.report_graph.subjects(rdflib.RDF.type, SH.ValidationResult):
        severity = self.report_graph.value(result, SH.resultSeverity)
        focus_node = self.report_graph.value(result, SH.focusNode)
        result_path = self.report_graph.value(result, SH.resultPath)
        value = self.report_graph.value(result, SH.value)
        source_shape = self.report_graph.value(result, SH.sourceShape)
        message = self.report_graph.value(result, SH.resultMessage)

        violations.append({
            "severity": self._shorten(severity),
            "focus_node": str(focus_node) if focus_node else "",
            "path": str(result_path) if result_path else "",
            "value": str(value) if value else "",
            "source_shape": str(source_shape) if source_shape else "",
            "message": str(message) if message else "",
        })

    return violations

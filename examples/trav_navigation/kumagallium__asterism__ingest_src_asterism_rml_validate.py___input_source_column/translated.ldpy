# Extracted from kumagallium/asterism@f0977d4d3a : ingest/src/asterism/rml_validate.py
# region: _input_source_column (lines 700-719, stratum trav_navigation)
# licence of the source repository: see meta.json
_REFERENCE_PREDS = (
    "http://w3id.org/rml/reference",
    "http://semweb.mmlab.be/ns/rml#reference",
)
_FUNCTION_EXECUTION_PREDS = (_RMLF + "functionExecution", _FNML_OLD + "functionExecution")
_INPUT_PREDS = (_RMLF + "input", _FNML_OLD + "input")
_INPUT_VALUE_MAP_PREDS = (_RMLF + "inputValueMap", _FNML_OLD + "inputValueMap")

def _input_source_column(graph, node) -> str | None:
    """The source column feeding an input-value map node: a direct
    ``rml:reference``, or — through a nested transform ``functionExecution`` —
    the first reference reachable below it (constants are not columns)."""
    import rdflib

    uri = rdflib.URIRef
    for rp in _REFERENCE_PREDS:
        for r in graph.objects(node, uri(rp)):
            return str(r)
    for fe_pred in _FUNCTION_EXECUTION_PREDS:
        for fe in graph.objects(node, uri(fe_pred)):
            for in_pred in _INPUT_PREDS:
                for inp in graph.objects(fe, uri(in_pred)):
                    for ivm_pred in _INPUT_VALUE_MAP_PREDS:
                        for ivm in graph.objects(inp, uri(ivm_pred)):
                            col = _input_source_column(graph, ivm)
                            if col is not None:
                                return col
    return None

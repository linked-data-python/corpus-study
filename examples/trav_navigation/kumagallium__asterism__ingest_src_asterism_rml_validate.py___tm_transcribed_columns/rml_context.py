# Context shim (see meta.json): subset of ingest/src/asterism/rml_validate.py
# from kumagallium/asterism@f0977d4d3a, so the region executes outside the
# package. Identical bindings for both representations.

_RMLF = "http://w3id.org/rml/"
_FNML_OLD = "http://semweb.mmlab.be/ns/fnml#"

_INPUT_PREDS = (_RMLF + "input", _FNML_OLD + "input")
_INPUT_VALUE_MAP_PREDS = (_RMLF + "inputValueMap", _FNML_OLD + "inputValueMap")


def _local_name(iri: str) -> str:
    """The trailing path/fragment segment of an IRI (for readable messages)."""
    tail = iri.rsplit("#", 1)[-1]
    return tail.rsplit("/", 1)[-1] or iri


def _fn_source_columns(graph, fe) -> set[str]:
    """Every distinct source column feeding a ``functionExecution``'s inputs.

    Recurses through nested function executions (a transform-of-a-transform),
    so ``f(g(col))`` still counts ``col`` once. A ``rr:constant``/``fn:constant``
    input contributes nothing — it is not a column at all. Used by
    :func:`_tm_transcribed_columns` to tell "this function reshapes ONE column's
    value" (still a transcription of that column) from "this function combines
    SEVERAL columns" (a derived value, not any one column's transcription)."""
    import rdflib

    uri = rdflib.URIRef
    cols: set[str] = set()
    for in_pred in _INPUT_PREDS:
        for inp in graph.objects(fe, uri(in_pred)):
            for ivm_pred in _INPUT_VALUE_MAP_PREDS:
                for ivm in graph.objects(inp, uri(ivm_pred)):
                    found = False
                    for rp in _REFERENCE_PREDS:
                        for r in graph.objects(ivm, uri(rp)):
                            cols.add(str(r))
                            found = True
                    if found:
                        continue
                    for fe_pred in _FUNCTION_EXECUTION_PREDS:
                        for nested_fe in graph.objects(ivm, uri(fe_pred)):
                            cols |= _fn_source_columns(graph, nested_fe)
    return cols


# Same reference/function-execution predicates as the region defines, so this
# shim's helper can resolve them without importing back from the caller.
_REFERENCE_PREDS = (
    "http://w3id.org/rml/reference",
    "http://semweb.mmlab.be/ns/rml#reference",
)
_FUNCTION_EXECUTION_PREDS = (_RMLF + "functionExecution", _FNML_OLD + "functionExecution")

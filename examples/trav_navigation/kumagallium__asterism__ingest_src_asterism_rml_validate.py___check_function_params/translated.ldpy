# Extracted from kumagallium/asterism@f0977d4d3a : ingest/src/asterism/rml_validate.py
# region: _check_function_params (lines 398-440, stratum trav_navigation)
# licence of the source repository: see meta.json
_FUNCTION_PREDS = (_RMLF + "function", _FNML_OLD + "function")
_INPUT_PREDS = (_RMLF + "input", _FNML_OLD + "input")
_PARAMETER_PREDS = (_RMLF + "parameter", _FNML_OLD + "parameter")

def _check_function_params(graph) -> list[str]:
    """Flag FnO executions that supply an unaccepted param or omit a required one.

    For each ``rmlf:functionExecution``: resolve its ``rmlf:function`` IRI to a
    registered Tier 0 spec, gather the supplied ``rmlf:parameter`` IRIs, then flag
    (a) any supplied parameter the function does not accept and (b) any required
    parameter the execution did not supply. A function IRI outside the Tier 0 set
    is left to :func:`asterism.rml_safety.assert_rml_safe`, not duplicated here.
    """
    import rdflib

    issues: list[str] = []
    specs = _required_param_iris()
    sub_pred = rdflib.URIRef

    for fe in _function_executions(graph):
        fun_iri: str | None = None
        for f_pred in _FUNCTION_PREDS:
            for f in graph.objects(fe, sub_pred(f_pred)):
                fun_iri = str(f)
        if fun_iri is None or fun_iri not in specs:
            continue  # unnamed, or non-Tier-0 (rml_safety handles the latter)
        meta = specs[fun_iri]
        fn_name = str(meta["name"])
        accepted: set[str] = meta["accepted"]  # type: ignore[assignment]
        required: set[str] = meta["required"]  # type: ignore[assignment]
        supplied: set[str] = set()
        for in_pred in _INPUT_PREDS:
            for inp in graph.objects(fe, sub_pred(in_pred)):
                for p_pred in _PARAMETER_PREDS:
                    for p in graph.objects(inp, sub_pred(p_pred)):
                        supplied.add(str(p))
        for extra in sorted(supplied - accepted):
            accepts = ", ".join(sorted(_local_name(a) for a in accepted)) or "(none)"
            issues.append(
                f"{fn_name} does not accept parameter {_local_name(extra)!r}; "
                f"it accepts: {accepts}."
            )
        for missing in sorted(required - supplied):
            issues.append(
                f"{fn_name} is missing required parameter {_local_name(missing)!r}."
            )
    return issues

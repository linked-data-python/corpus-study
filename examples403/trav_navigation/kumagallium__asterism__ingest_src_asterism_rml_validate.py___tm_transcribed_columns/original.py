# Extracted from kumagallium/asterism@f0977d4d3a : ingest/src/asterism/rml_validate.py
# region: _tm_transcribed_columns (lines 1002-1037, stratum trav_navigation)
# licence of the source repository: see meta.json
_REFERENCE_PREDS = (
    "http://w3id.org/rml/reference",
    "http://semweb.mmlab.be/ns/rml#reference",
)
_FUNCTION_EXECUTION_PREDS = (_RMLF + "functionExecution", _FNML_OLD + "functionExecution")
_R2RML = "http://www.w3.org/ns/r2rml#"
_TERM_TYPE_PREDS = (_R2RML + "termType", _RMLF + "termType")

def _tm_transcribed_columns(graph, tm) -> set[str]:
    """Columns this map TRANSCRIBES onto a literal object: a plain fact copied
    from exactly one source cell, however it got there.

    A object map is a transcription of column X when it holds:
    - a direct ``rml:reference`` to X (exactly the shape the IR compiler emits
      for ``column:``), or
    - a function pipeline whose inputs read EXACTLY ONE distinct source column
      (constants don't count as columns; nested transforms are followed) —
      ``number_clean(X)`` is still X's value, just reshaped, so it is X's
      transcription too. A function combining TWO OR MORE columns produces a
      genuinely derived value that belongs to none of its inputs alone, so it
      is excluded (an ``rr:termType rr:IRI`` object map is a link/ID, never a
      transcription, and is excluded outright)."""
    import rdflib

    uri = rdflib.URIRef
    out: set[str] = set()
    for pom in graph.objects(tm, uri(_R2RML + "predicateObjectMap")):
        for om in graph.objects(pom, uri(_R2RML + "objectMap")):
            is_iri = any(
                _local_name(str(t)) == "IRI"
                for tp in _TERM_TYPE_PREDS
                for t in graph.objects(om, uri(tp))
            )
            if is_iri:
                continue
            for rp in _REFERENCE_PREDS:
                for r in graph.objects(om, uri(rp)):
                    out.add(str(r))
            for fe_pred in _FUNCTION_EXECUTION_PREDS:
                for fe in graph.objects(om, uri(fe_pred)):
                    cols = _fn_source_columns(graph, fe)
                    if len(cols) == 1:
                        out |= cols
    return out

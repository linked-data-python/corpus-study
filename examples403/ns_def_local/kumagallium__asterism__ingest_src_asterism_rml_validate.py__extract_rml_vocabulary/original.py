# Extracted from kumagallium/asterism@f0977d4d3a : ingest/src/asterism/rml_validate.py
# region: extract_rml_vocabulary (lines 1745-1772, stratum ns_def_local)
# licence of the source repository: see meta.json
_TTL_PREFIX = re.compile(r"(?im)^\s*@?prefix\s+([A-Za-z][\w.-]*)?\s*:\s*<([^>]+)>")

def extract_rml_vocabulary(rml_ttl: str) -> dict[str, object]:
    """The closed vocabulary a mapping materializes: prefixes + class/predicate IRIs.

    Deterministic ground truth for anything that must speak the dataset's real
    schema (e.g. an AI-drafted query tool): ``rr:class`` objects and
    ``rr:predicate`` objects ARE the terms that exist in the ingested data —
    a term outside this set matches nothing. Returns
    ``{"prefixes": {label: iri}, "terms": set[str]}``; empty structures when the
    RML is missing/unparseable (callers degrade to "no oracle" gracefully).
    """
    prefixes: dict[str, str] = {
        (m.group(1) or ""): m.group(2) for m in _TTL_PREFIX.finditer(rml_ttl or "")
    }
    terms: set[str] = set()
    if (rml_ttl or "").strip():
        import rdflib

        graph = rdflib.Graph()
        try:
            graph.parse(data=rml_ttl, format="turtle")
        except Exception:
            return {"prefixes": {}, "terms": set()}
        rr = rdflib.Namespace("http://www.w3.org/ns/r2rml#")
        for obj in graph.objects(None, rr["class"]):
            terms.add(str(obj))
        for obj in graph.objects(None, rr.predicate):
            terms.add(str(obj))
    return {"prefixes": prefixes, "terms": terms}

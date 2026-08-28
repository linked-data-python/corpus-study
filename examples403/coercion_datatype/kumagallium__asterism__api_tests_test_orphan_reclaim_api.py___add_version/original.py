# Extracted from kumagallium/asterism@f0977d4d3a : api/tests/test_orphan_reclaim_api.py
# region: _add_version (lines 73-74, stratum coercion_datatype)
# licence of the source repository: see meta.json
import rdflib
_EX = rdflib.Namespace("https://ex#")

def _add_version(ds: rdflib.Dataset, iri: str) -> None:
    ds.graph(rdflib.URIRef(iri)).add((_EX.s, _EX.p, rdflib.Literal(iri)))

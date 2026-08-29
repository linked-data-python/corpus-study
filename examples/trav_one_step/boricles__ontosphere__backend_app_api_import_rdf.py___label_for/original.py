# Extracted from boricles/ontosphere@e055553268 : backend/app/api/import_rdf.py
# region: _label_for (lines 56-62, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import Graph as RdfGraph
from rdflib.namespace import OWL, RDF, RDFS

def _label_for(g: RdfGraph, subject, uri_str: str) -> str:  # type: ignore[type-arg]
    """Return rdfs:label if present, otherwise the local name from the URI."""
    val = g.value(subject, RDFS.label)
    if val:
        return str(val)
    fragment = uri_str.rsplit("#", 1)[-1].rsplit("/", 1)[-1]
    return fragment or uri_str

# Context shim (see meta.json): ``fetch`` is a module-level helper of
# pylode/profiles/supermodel/loader.py in RDFLib/pyLODE@0d0471fb99 that the
# extracted region calls.  The real one performs an HTTP GET with httpx; here
# it serves a small fixed set of documents from memory, so the region runs
# without network access.  Same signature, same (text, content_type) result.
# Used IDENTICALLY by original.py and translated.ldpy.

MEDIA_TYPES = {
    "text/turtle": "text/turtle",
    "application/n-triples": "application/n-triples",
    "application/n-quads": "application/n-quads",
}

DOCUMENTS = {
    "http://example.org/onto/base": """
        @prefix owl:  <http://www.w3.org/2002/07/owl#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        <http://example.org/onto/base> a owl:Ontology ;
            owl:imports <http://example.org/onto/leaf> ;
            rdfs:label "base" .
    """,
    "http://example.org/onto/leaf": """
        @prefix owl:  <http://www.w3.org/2002/07/owl#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        <http://example.org/onto/leaf> a owl:Ontology ;
            rdfs:label "leaf" .
    """,
    "http://example.org/onto/broken": "this is not turtle @@@",
}


def fetch(url: str, client=None, content_type: str = "text/turtle"):
    if url not in DOCUMENTS:
        raise RuntimeError("HTTP 404: no such resource %s" % url)
    return DOCUMENTS[url], content_type

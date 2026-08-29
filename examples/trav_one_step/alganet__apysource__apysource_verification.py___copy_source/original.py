# Extracted from alganet/apysource@f800ec97c1 : apysource/verification.py
# region: _copy_source (lines 91-110, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, RDF, XSD

def _copy_source(into: Graph, g: Graph, source: URIRef, depth: int = 3) -> None:
    """Copy a source's description, and its parents' with it.

    A concise bounded description stops at a named node, so `dcterms:isPartOf`
    was copied as a bare reference to a parent that appeared nowhere else in the
    file — no type, no label, no url. Which meant the emitted provenance failed
    apysource's own `SourceShape` (`dcterms:isPartOf must point at a sv:Source`):
    the very dangling-reference problem this copying was added to fix, one level
    further up, and only visible once the shapes were actually run.

    A chapter names its book, and the book may name a series; ``depth`` bounds it
    the way ``_resolve_source_url`` bounds the same walk, since a graph is free to
    contain a cycle.
    """
    if depth <= 0 or (source, None, None) in into:
        return
    into += g.cbd(source)
    for parent in g.objects(source, DCTERMS.isPartOf):
        if isinstance(parent, URIRef):
            _copy_source(into, g, parent, depth - 1)

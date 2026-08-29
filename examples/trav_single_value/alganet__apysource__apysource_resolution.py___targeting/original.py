# Extracted from alganet/apysource@f800ec97c1 : apysource/resolution.py
# region: _targeting (lines 131-155, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS
from apysource.namespaces import OA, SCHEMA, SV

def _targeting(g: Graph, frag_uri: URIRef,
               format_holder: URIRef) -> tuple[str, str | None]:
    """What this fragment says to target, and in what format.

    Read the same way no matter who will serve the document. It used to be read
    only on the fetcher branch, so a ``section:`` on a repo-backed fragment was
    dropped without a word — and a fragment naming a section the document does
    not have verified **green**, because the repo handed back the whole page and
    the snippet turned up somewhere in it. Whether a citation was checked against
    the section it named depended on whether a repo happened to claim its URL.
    """
    section = _get_selector_value(g, frag_uri, SV.SectionSelector)
    if section:
        return "section", section

    # Deliberately *not* normalized here, though it looks like it should be.
    # `_find_format` already matches an internal name ("html", "plain-text")
    # before it tries MIME, so a Turtle author writing `dcterms:format "html"`
    # was always understood, and normalizing first would only throw away the
    # more specific of the two answers. A name says which reader; a media type
    # says which family of readers, and several may still answer to one.
    format_name = str(g.value(format_holder, DCTERMS.format) or "")
    css = _get_selector_value(g, frag_uri, OA.CssSelector)
    lines = str(g.value(frag_uri, SV.sourceLines) or "")
    return format_name, (css or lines) or None

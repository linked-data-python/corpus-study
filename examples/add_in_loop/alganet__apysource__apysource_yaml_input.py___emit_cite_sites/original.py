# Extracted from alganet/apysource@f800ec97c1 : apysource/yaml_input.py
# region: _emit_cite_sites (lines 238-296, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, PROV, RDF, RDFS
from apysource.namespaces import OA, SV, new_graph
from apysource.schema import (  # noqa: F401 — the vocabulary lives here now
    _CITE_SITE_ALLOWED,
    _FRAGMENT_ALLOWED,
    _FRAGMENT_KEYS,
    _NORMALIZE_KEYS,
    _SOURCE_ALLOWED,
    _SOURCE_KEYS,
    _TOP_ALLOWED,
    FRAGMENT_KEYS,
    SOURCE_KEYS,
    TARGETTING_KEYS,
    reject_unknown_keys,
    text,
)
_reject_unknown_keys = reject_unknown_keys
_text = text

def _emit_cite_sites(g: Graph, frag_uri: URIRef, frag_def: dict[str, object],
                     what: str) -> None:
    """Emit the *citing* side: the places that make this claim.

    ``prov:wasDerivedFrom`` points from the cite site to the fragment, and that
    direction is the true one — the line of code was derived from the normative
    sentence, not the other way round. ``sv:citedBy`` is the same edge walked
    backwards, so a report holding a fragment can find its sites without a
    reverse scan of the graph.

    A ``cited_by:`` written as a single mapping rather than a list of them is
    refused rather than wrapped. Guessing would be free here, and it is exactly
    the guess that turns one dropped entry into a citation nobody is told about.
    """
    sites = frag_def.get("cited_by")
    if sites is None:
        return

    if not isinstance(sites, list):
        raise ValueError(
            f"{what}: cited_by must be a list of places, not a "
            f"{type(sites).__name__}. Write it as a list even when there is "
            f"only one — a single mapping is one entry away from silently "
            f"becoming none.",
        )

    for i, site in enumerate(sites, 1):
        where = f"{what}: cited_by[{i}]"
        if not isinstance(site, dict):
            raise ValueError(
                f"{where} must be a mapping with a 'file', not a "
                f"{type(site).__name__}.",
            )
        _reject_unknown_keys(site, _CITE_SITE_ALLOWED, where)

        file = site.get("file")
        if not file:
            raise ValueError(
                f"{where}: a cite site must name the 'file' it is in. A site "
                f"with no place is not a place.",
            )

        # Numbered by position in the list, which `_dedupe`-style callers keep
        # sorted, so a site added in the middle does not relabel the ones after it.
        node = _anon(frag_uri, f"cite_{i}")
        g.add((node, RDF.type, SV.CiteSite))
        g.add((node, SV.citingFile, Literal(_text(file, f"{where}: file"))))
        g.add((node, PROV.wasDerivedFrom, frag_uri))
        g.add((frag_uri, SV.citedBy, node))

        line = site.get("line")
        if line is not None:
            # bool is an int in Python, and `line: true` is not line 1.
            if not isinstance(line, int) or isinstance(line, bool):
                raise ValueError(
                    f"{where}: line must be a whole number, not a "
                    f"{type(line).__name__}.",
                )
            g.add((node, SV.citingLine, Literal(line)))

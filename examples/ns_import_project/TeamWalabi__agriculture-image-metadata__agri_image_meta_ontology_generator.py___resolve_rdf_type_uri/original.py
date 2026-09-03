# Extracted from TeamWalabi/agriculture-image-metadata@d34fe77241 : agri_image_meta/ontology/generator.py
# region: _resolve_rdf_type_uri (lines 49-66, stratum ns_import_project)
# licence of the source repository: see meta.json
#
# Executability restoration (AGENT_BATCH "163 regions" case, see meta.json):
# `agri_image_meta.utils.namespaces` rewritten to `agri_image_meta_ns`, the
# shim module next to this file (the real `agri_image_meta` package is not
# on PyPI, so it cannot be installed to run this extracted file standalone;
# the shim's six IRIs are transcribed verbatim from the real
# namespaces.py at the pinned commit -- see its header).
from rdflib import Graph, RDF, RDFS, OWL, URIRef, Literal, BNode, XSD
from agri_image_meta_ns import AGIMAGE, SH, DCT, FOAF, SOSA, EXIF

def _resolve_rdf_type_uri(rdf_type_str):
    """
    Resolve a prefixed rdf_type string (e.g. 'sosa:Sensor') to a URIRef.

    Returns None if it resolves to the agimage namespace.
    """
    if not rdf_type_str or ":" not in rdf_type_str:
        return None
    prefix, local = rdf_type_str.split(":", 1)
    ns_map = {
        "sosa": SOSA,
        "foaf": FOAF,
        "dcat": URIRef("http://www.w3.org/ns/dcat#"),
    }
    ns = ns_map.get(prefix)
    if ns is None:
        return None
    return URIRef(str(ns) + local)

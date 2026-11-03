# Extracted from d3fend/d3fend-ontology@cce593d61c : src/util/update_atlas.py
# region: add_revoked (lines 218-247, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import Literal, Namespace, URIRef
from build import _xmlns as _XMLNS
owl = Namespace("http://www.w3.org/2002/07/owl#")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")

def add_revoked(graph, tech):
    revoked_by = tech["revoked_by"]
    atlas_id = next((ref.get("external_id") for ref in tech["data"]["external_references"]
                     if ref.get("source_name") == "mitre-atlas"), None)
    atlas_uri = URIRef(_XMLNS + atlas_id)

    # Check if tech already has revoked annotations
    if (None, None, Literal(atlas_id)) in graph and (atlas_uri, owl.deprecated, None) not in graph:
        # Add a triple indicating deprecation
        graph += [
            (atlas_uri, rdfs.seeAlso, Literal(revoked_by)),
            (atlas_uri, owl.deprecated, Literal(True)),
            (atlas_uri, rdfs.comment, Literal(f"This technique has been revoked by {revoked_by}")),
        ]
        return 1
    return 0

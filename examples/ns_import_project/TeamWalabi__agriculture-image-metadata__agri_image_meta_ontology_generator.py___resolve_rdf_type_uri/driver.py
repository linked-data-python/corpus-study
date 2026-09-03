"""Validation driver for TeamWalabi__agriculture-image-metadata__agri_image_meta_ontology_generator.py___resolve_rdf_type_uri.

`_resolve_rdf_type_uri` is a pure function of one string, returning a
URIRef or None -- the return value IS the oracle. Cases cover: each of the
three prefixes in `ns_map` (sosa, foaf, dcat -- exercising both the
`@prefix … as NAME` object and the bare-IRI `dcat` entry), the
docstring-highlighted 'agimage' case (resolves to None because "agimage"
is not a key of ns_map, not because of a dedicated check -- confirmed
directly against original.py's own logic), an unknown prefix, a string
with no ':' at all, and the empty string.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='_resolve_rdf_type_uri',
    calls=[
        (("sosa:Sensor",), {}),
        (("foaf:Person",), {}),
        (("dcat:Dataset",), {}),
        (("agimage:ImageObservation",), {}),
        (("unknown:Thing",), {}),
        (("NoColonHere",), {}),
        (("",), {}),
    ],
)

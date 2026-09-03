"""Validation driver for gtfierro__rdf-mcp__rdf_mcp_servers_s223_server.py__get_possible_properties.

EXCLUDED (see meta.json): `ontology = Graph().parse("https://open223.info/223p.ttl")`
is a MODULE-LEVEL live network fetch of a real, third-party ontology file --
present unconditionally in the region's own context lines, not something a
fixture could substitute without changing what the region actually does.
Both original.py and translated.ldpy re-fetch it on every run of this
driver, so the pilot is not evaluable "in isolation" (design record
corpus/403, revision of 2026-08-29: "7 régions ... non évaluables en
isolation (service réseau, base, paquet du dépôt d'origine)") -- it depends
on a live endpoint that can be slow, down, or have changed its content
between two runs, which is exactly the category that record's classification
excludes from the measured results, whether or not the endpoint happens to
answer right now.

The calls below were nonetheless exercised by hand against the live
ontology while writing this translation (network reachable in this
environment at the time) and DID agree between original.py and
translated.ldpy -- "Zone" resolves to 5 property paths via the
`rdfs:subClassOf*` walk, "NoSuchClass223Term" to zero -- which is evidence
the translation is faithful, not a claim that this driver is fit to decide
`translation_status: final` on its own account (it isn't; see meta.json).
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='get_possible_properties',
    calls=[
        (("Zone",), {}),
        (("NoSuchClass223Term",), {}),
    ],
)

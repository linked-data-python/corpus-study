# Extracted from laBioSynCare/laBioSynCare.github.io@6dd8224b03 : scripts/check-signal-layer.py
# region: main (lines 223-226, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, RDF, URIRef
SSTIM = Namespace("https://w3id.org/sstim#")

bands_with_bounds = sum(
    1 for b in graph.subjects(RDF.type, SSTIM.FrequencyBand)
    if list(graph.objects(b, SSTIM.hzMin)) and list(graph.objects(b, SSTIM.hzMax))
)

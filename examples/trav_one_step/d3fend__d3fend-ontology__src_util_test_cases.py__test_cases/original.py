# Extracted from d3fend/d3fend-ontology@cce593d61c : src/util/test_cases.py
# region: test_cases (lines 198-198, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import URIRef, Literal, Graph, RDF, RDFS, Namespace
from build import _xmlns as _XMLNS
d3fend = Namespace("http://d3fend.mitre.org/ontologies/d3fend.owl#")

_assert(g.value(URIRef(_XMLNS + "T1026"), d3fend["attack-id"]), Literal("T1026"))

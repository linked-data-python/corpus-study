# Extracted from technologiestiftung/digital-budget-network-explorer@a2c69bf9f4 : preprocess_graph.py
# region: first_label (lines 74-79, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, RDF
from rdflib.namespace import SKOS, OWL, DCTERMS, RDFS
SCHEMA = Namespace("https://schema.org/")

def first_label(g: Graph, subj) -> str | None:
    for pred in (SKOS.prefLabel, SCHEMA.name, RDFS.label):
        val = g.value(subj, pred)
        if val is not None:
            return str(val)
    return None

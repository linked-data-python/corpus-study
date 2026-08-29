# Extracted from emmo-repo/domain-electrochemistry@588dffa71e : .github/scripts/check_iri_resolution.py
# region: ontology_subject (lines 70-73, stratum trav_one_step)
# licence of the source repository: see meta.json
import rdflib

def ontology_subject(graph: rdflib.Graph, source: str) -> rdflib.URIRef:
    for subject in graph.subjects(rdflib.RDF.type, rdflib.OWL.Ontology):
        return subject
    raise RuntimeError(f"{source}: no owl:Ontology declaration found")

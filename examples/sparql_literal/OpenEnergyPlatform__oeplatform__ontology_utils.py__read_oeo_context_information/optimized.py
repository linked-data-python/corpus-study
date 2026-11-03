# Extracted from OpenEnergyPlatform/oeplatform@ff28ef6390 : ontology/utils.py
# region: read_oeo_context_information (lines 141-206, stratum sparql_literal)
# licence of the source repository: see meta.json
from collections import defaultdict
from typing import Iterable
from rdflib import Graph
from rdflib.query import ResultRow
from oeplatform.settings import OEO_EXT_NAME, ONTOLOGY_ROOT, OPEN_ENERGY_ONTOLOGY_NAME

def read_oeo_context_information(path, file, ontology=None):
    g = Graph().parse((path / file).as_posix())

    classes_name = {s.split("/")[-1]: o
                    for s, o in g.query("SELECT DISTINCT ?s ?o WHERE { ?s rdfs:label ?o }")}

    ontology_description = ""
    for s, o in g.query("SELECT ?s ?o WHERE { ?s dc:description ?o }"):
        if s.split("/")[-1] == "":
            ontology_description = o

    classes_definitions = defaultdict(list)
    classes_notes = defaultdict(list)
    if ontology == OPEN_ENERGY_ONTOLOGY_NAME:
        for s, o in g.query("SELECT DISTINCT ?s ?o WHERE { ?s obo:IAO_0000115 ?o }"):
            classes_definitions[s.split("/")[-1]].append(o)
        for s, o in g.query("SELECT DISTINCT ?s ?o WHERE { ?s obo:IAO_0000116 ?o }"):
            classes_notes[s.split("/")[-1]].append(o)

    return {
        "q_global": g.query(
            "SELECT DISTINCT ?s ?o WHERE { ?s rdfs:subClassOf ?o filter(!isBlank(?o)) }"),
        "classes_name": classes_name,
        "classes_definitions": dict(classes_definitions),
        "classes_notes": dict(classes_notes),
        "ontology_description": ontology_description,
    }

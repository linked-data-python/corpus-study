# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/tests/owl2vt/compare_vt_output.py
# region: load_without_ontology_header (lines 35-41, stratum remove)
# licence of the source repository: see meta.json
from rdflib import Graph
from rdflib.namespace import OWL, RDF

def load_without_ontology_header(path):
    g = Graph()
    g.parse(path, format='turtle')
    for ontology in list(g.subjects(RDF.type, OWL.Ontology)):
        for p, o in list(g.predicate_objects(ontology)):
            g.remove((ontology, p, o))
    return g

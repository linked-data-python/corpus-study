# Extracted from unibz-core/Scior@1d9f010224 : scior/modules/utils_rdf.py
# region: get_ontology_uri (lines 120-125, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import RDF, OWL, Graph

def get_ontology_uri(ontology_graph):
    """ Return the URI of the ontology graph. """

    ontology_uri = ontology_graph.value(predicate=RDF.type, object=OWL.Ontology)

    return ontology_uri

# Extracted from semanticarts/ontology-toolkit@99a1a00917 : onto_tool/onto_tool.py
# region: set_version (lines 28-37, stratum remove)
# licence of the source repository: see meta.json
import logging
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import OWL, XSD

def set_version(g, ontology, ontology_iri, version):
    """Add or replace versionIRI for the specified ontology."""
    old_version = next(g.objects(ontology, OWL.versionIRI), None)
    if old_version:
        logging.debug(f'Removing versionIRI {old_version} from {ontology}')
        g.remove((ontology, OWL.versionIRI, old_version))

    version_iri = URIRef(f"{ontology_iri}{version}")
    g.add((ontology, OWL.versionIRI, version_iri))
    logging.info(f'versionIRI {version_iri} added for {ontology}')

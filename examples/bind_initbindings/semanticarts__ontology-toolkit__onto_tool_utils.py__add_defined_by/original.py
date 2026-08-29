# Extracted from semanticarts/ontology-toolkit@99a1a00917 : onto_tool/utils.py
# region: add_defined_by (lines 47-96, stratum bind_initbindings)
# licence of the source repository: see meta.json
import logging
from rdflib.namespace import OWL, RDF, RDFS, SKOS, XSD

def add_defined_by(g, ontology_iri, mode='strict', replace=False, versioned=False):
    """Add rdfs:isDefinedBy to every entity declared by the ontology."""
    if versioned:
        version_iri = next(g.objects(ontology_iri, OWL.versionIRI), None)
        if version_iri is not None:
            ontology_iri = version_iri
    if mode == 'strict':
        selector = """
          FILTER(?dtype IN (
            owl:Class, owl:ObjectProperty, owl:DatatypeProperty,
            owl:AnnotationProperty, owl:Thing
          ))
        """
    else:
        selector = "FILTER(?dtype != owl:Ontology)"

    query = """
        SELECT distinct ?defined ?label ?defBy WHERE {
          ?defined a ?dtype .
          %s
          FILTER(!ISBLANK(?defined))
          FILTER EXISTS {
            ?defined ?anotherProp ?value .
            FILTER (?anotherProp != rdf:type)
          }
          OPTIONAL { ?defined rdfs:isDefinedBy ?defBy }
        }
        """ % selector

    definitions = g.query(
        query,
        initNs={'owl': OWL, 'rdfs': RDFS, 'skos': SKOS})
    for d in definitions:
        if d.defBy:
            if d.defBy == ontology_iri:
                logging.debug('%s already defined by %s',
                              d.defined, ontology_iri)
            else:
                if replace:
                    logging.debug(
                        'Replaced definedBy for %s to %s',
                        d.defined, ontology_iri)
                    g.remove((d.defined, RDFS.isDefinedBy, d.defBy))
                    g.add((d.defined, RDFS.isDefinedBy, ontology_iri))
                else:
                    logging.warning('%s defined by %s instead of %s',
                                    d.defined, d.defBy, ontology_iri)
        else:
            logging.debug('Added definedBy to %s', d.defined)
            g.add((d.defined, RDFS.isDefinedBy, ontology_iri))

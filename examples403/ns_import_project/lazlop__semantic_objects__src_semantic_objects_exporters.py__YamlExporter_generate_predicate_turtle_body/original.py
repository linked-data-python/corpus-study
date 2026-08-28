# Extracted from lazlop/semantic_objects@243c5efd8c : src/semantic_objects/exporters.py
# region: YamlExporter.generate_predicate_turtle_body (lines 98-116, stratum ns_import_project)
# licence of the source repository: see meta.json
from .namespaces import PARAM, RDF, RDFS, SH, XSD, bind_prefixes
from rdflib import Graph, Literal, BNode, URIRef

@staticmethod
def generate_predicate_turtle_body(cls, subject_name="name", target_name="target"):
    """Generate RDF/Turtle body for Predicate template"""
    g = Graph()
    bind_prefixes(g)

    prop_iri = cls._get_iri()

    g.add((PARAM[subject_name], prop_iri, PARAM[target_name]))

    if cls._domain is not None:
        domain_iri = cls._domain._get_iri()
        g.add((prop_iri, RDFS.domain, domain_iri))

    if cls._range is not None:
        range_iri = cls._range._get_iri()
        g.add((prop_iri, RDFS.range, range_iri))

    return g.serialize(format='ttl')

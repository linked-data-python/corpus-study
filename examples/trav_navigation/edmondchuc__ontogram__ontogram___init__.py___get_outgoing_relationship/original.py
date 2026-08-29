# Extracted from edmondchuc/ontogram@777ea837bc : ontogram/__init__.py
# region: _get_outgoing_relationship (lines 171-196, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib.namespace import RDF, OWL, RDFS, DCTERMS

def _get_outgoing_relationship(g):
    plant_uml = ''

    classes = _get_classes(g)

    for rdf_property, _, _ in g.triples((None, RDF.type, RDF.Property)):
        for _, _, rdfs_domain in g.triples((rdf_property, RDFS.domain, None)):
            for _, _, rdfs_range in g.triples((rdf_property, RDFS.range, None)):
                if rdfs_range in classes:
                    domain_namespace = _get_uri_namespace(rdfs_domain)
                    domain_prefix = _get_uri_prefix(domain_namespace, g)
                    domain_name = _get_last_segment_of_uri(rdfs_domain)

                    relationship_namespace = _get_uri_namespace(rdf_property)
                    relationship_prefix = _get_uri_prefix(relationship_namespace, g)
                    relationship_name = _get_last_segment_of_uri(rdf_property)

                    range_namespace = _get_uri_namespace(rdfs_range)
                    range_prefix = _get_uri_prefix(range_namespace, g)
                    range_name = _get_last_segment_of_uri(rdfs_range)

                    plant_uml += f'"{domain_prefix}:{domain_name}" --> "{range_prefix}:{range_name}" : "[[{str(rdf_property)} {relationship_prefix}:{relationship_name}]]"\n'
                break
            break

    return plant_uml

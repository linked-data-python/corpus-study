# Extracted from lazlop/semantic_objects@243c5efd8c : src/semantic_objects/exporters.py
# region: RdfExporter.generate_rdf_class_definition (lines 622-657, stratum add_isolated)
# licence of the source repository: see meta.json
from .namespaces import PARAM, RDF, RDFS, SH, XSD, bind_prefixes
from rdflib import Graph, Literal, BNode, URIRef

for base_class in classes_to_process:
    if not hasattr(base_class, '_valid_relations'):
        continue

    for relation, target_class in base_class._valid_relations:
        relation_key = relation._name
        if relation_key in processed_relations:
            continue
        processed_relations.add(relation_key)

        relation_iri = relation._get_iri()

        prop_node = BNode()
        g.add((class_iri, SH.property, prop_node))
        g.add((prop_node, RDF.type, SH.PropertyShape))
        g.add((prop_node, SH.path, relation_iri))

        if target_class is None:
            target_class_name = "None"
        elif target_class.__name__ == 'Self' or str(target_class) == 'Self':
            target_class_name = cls.__name__
            target_class = cls
        elif hasattr(target_class, '__name__'):
            target_class_name = target_class.__name__
        else:
            target_class_name = str(target_class)

        field_comment = f"If the relation `{relation._name}` is present it must associate the `{cls.__name__}` with a `{target_class_name}`."
        g.add((prop_node, RDFS.comment, Literal(field_comment)))

        if hasattr(target_class, '_get_iri'):
            target_class_iri = target_class._get_iri()
            g.add((prop_node, SH['class'], target_class_iri))

            message = f"s223: If the relation `{relation._name}` is present it must associate the `{cls.__name__}` with a `{target_class_name}`."
            g.add((prop_node, SH.message, Literal(message)))

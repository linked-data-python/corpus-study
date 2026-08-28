# Extracted from OntoUML/ontouml-json2graph@982f12b9c4 : json2graph/decoder/decode_obj_property.py
# region: set_cardinality_relations (lines 214-273, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, RDF, Literal, XSD
from ..modules import arguments as args
from ..modules.utils_graph import load_ontouml_vocabulary, ontouml_ref

def set_cardinality_relations(property_dict: dict, ontouml_graph: Graph) -> None:
    """Create the ontouml:Cardinality instance and sets its properties.

    :param property_dict: Property object loaded as a dictionary.
    :type property_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """
    if "cardinality" in property_dict:
        # Resolve before changing the graph so error policy aborts without creating a partial Cardinality individual.
        full_cardinality, lower_bound, upper_bound = determine_cardinality_bounds(
            property_dict["cardinality"], property_dict["id"]
        )

        ontology_property_individual = URIRef(args.ARGUMENTS["base_uri"] + property_dict["id"])
        ontology_cardinality_individual = URIRef(args.ARGUMENTS["base_uri"] + property_dict["id"] + "_cardinality")

        ontouml_cardinality_class = ontouml_ref("Cardinality")
        ontouml_cardinality_property = ontouml_ref("cardinality")

        ontouml_cardinalityvalue_property = ontouml_ref("cardinalityValue")
        ontouml_lowerbound_property = ontouml_ref("lowerBound")
        ontouml_upperbound_property = ontouml_ref("upperBound")

        # Creating ontouml:Cardinality individuals (named after its related Property's name + '_cardinality' string)
        ontouml_graph.add((ontology_cardinality_individual, RDF.type, ontouml_cardinality_class))

        # Setting the ontouml:cardinality between an ontouml:Property and its ontouml:Cardinality
        ontouml_graph.add(
            (
                ontology_property_individual,
                ontouml_cardinality_property,
                ontology_cardinality_individual,
            )
        )

        # Always preserve a Cardinality individual and its source or repaired cardinalityValue.
        ontouml_graph.add(
            (
                ontology_cardinality_individual,
                ontouml_cardinalityvalue_property,
                Literal(full_cardinality),
            )
        )
        # Bounds are emitted only for valid or successfully repaired values.
        if lower_bound is not None and upper_bound is not None:
            ontouml_graph.add(
                (
                    ontology_cardinality_individual,
                    ontouml_lowerbound_property,
                    Literal(lower_bound, datatype=XSD.nonNegativeInteger),
                )
            )
            ontouml_graph.add(
                (
                    ontology_cardinality_individual,
                    ontouml_upperbound_property,
                    Literal(upper_bound),
                )
            )

# Extracted from OntoUML/ontouml-json2graph@982f12b9c4 : json2graph/decoder/decode_main.py
# region: decode_dictionary (lines 27-115, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, Literal, RDF, XSD
from ontouml_shim import args, ontouml_ref, warn_if_text_value_is_unsupported, initialize_logger
LOGGER = initialize_logger()

def decode_dictionary(dictionary_data: dict, ontouml_graph: Graph, language: str) -> None:
    """Receive the full dictionary with the loaded JSON data and decode known allowed values to the OntoUML Graph.

    Recursively evaluates the dictionary to create all possible instances, setting their types and attributes.

    OntoUML-Vocabulary properties that are directly decoded in the general decoder:
        - description, height, isAbstract, isComplete, isDerived, isDisjoint, isOrdered, isReadOnly, name, width

    Restricted properties (the ones in the restricted_fields list) are not treated in this function.

    :param dictionary_data: Dictionary to have its fields decoded.
    :type dictionary_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    :param language: Language tag to be added to the ontology's concepts.
    :type language: str
    """
    restricted_fields = [
        "aggregationKind",
        "cardinality",
        "isExtensional",
        "isPowertype",
        "order",
        "stereotype",
        "x",
        "y",
    ]

    # Treating Path sub dictionaries
    if "id" not in dictionary_data:
        return

    # Creating instance
    new_instance = URIRef(args.ARGUMENTS["base_uri"] + dictionary_data["id"])

    # Setting instance type
    ontouml_graph.add((new_instance, RDF.type, ontouml_ref(dictionary_data["type"])))

    # Adding other attributes
    for key, value in dictionary_data.items():
        # if id or type was already treated, skip
        # If it is of a restricted field, do not add other attributes now
        if key in ("id", "type") or key in restricted_fields:
            continue

        # A legacy Text.value field has no equivalent in OntoUML Vocabulary v1.1.1.
        # Empty values are omitted silently; non-empty values are omitted with a warning.
        if key == "value" and dictionary_data["type"] == "Text":
            warn_if_text_value_is_unsupported(dictionary_data)
            continue

        # Recursively treats sub-dictionaries inside lists
        if type(value) is list:
            for item in value:
                if type(item) is dict:
                    decode_dictionary(item, ontouml_graph, language)
            continue

        # Recursively treats sub-dictionaries
        if type(value) is dict:
            decode_dictionary(value, ontouml_graph, language)
            continue

        # Graph's OBJECT definition
        if key == "name" and language:
            new_object = Literal(value, lang=language)
        elif key in ("width", "height"):
            if type(value) is not int or value < 0:
                LOGGER.error(
                    f"The object with ID {dictionary_data['id']} has an invalid value for its field '{key}' "
                    f"and was not transformed (expected a non-negative integer, received {value!r})."
                )
                continue
            new_object = Literal(value, datatype=XSD.nonNegativeInteger)
        else:
            new_object = Literal(value)

        # Adding to graph
        ontouml_graph.add((new_instance, ontouml_ref(key), new_object))

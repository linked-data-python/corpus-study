# Extracted from OntoUML/ontouml-json2graph@982f12b9c4 : json2graph/decoder/decode_obj_class.py
# region: set_class_restrictedto_ontologicalnature (lines 294-324, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, XSD, Literal
import ontouml_shim as args
from ontouml_shim import ontouml_ref


def set_class_restrictedto_ontologicalnature(class_dict: dict, ontouml_graph: Graph) -> None:
    """Set the ontouml:restrictedTo relation between a class and its related ontouml:OntologicalNature instance.

    :param class_dict: Class object loaded as a dictionary.
    :type class_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """
    restriction_nature_mapping = {
        "abstract": "abstractNature",
        "collective": "collectiveNature",
        "event": "eventNature",
        "extrinsic-mode": "extrinsicModeNature",
        "functional-complex": "functionalComplexNature",
        "intrinsic-mode": "intrinsicModeNature",
        "quality": "qualityNature",
        "quantity": "quantityNature",
        "relator": "relatorNature",
        "situation": "situationNature",
        "type": "typeNature",
    }

    if "restrictedTo" in class_dict:
        for restriction in class_dict["restrictedTo"]:
            ontouml_graph.add(
                (
                    URIRef(args.ARGUMENTS["base_uri"] + class_dict["id"]),
                    ontouml_ref("restrictedTo"),
                    ontouml_ref(restriction_nature_mapping[restriction]),
                )
            )

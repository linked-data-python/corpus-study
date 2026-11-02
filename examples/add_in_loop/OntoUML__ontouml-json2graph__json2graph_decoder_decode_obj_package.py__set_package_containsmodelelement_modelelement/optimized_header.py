# Extracted from OntoUML/ontouml-json2graph@982f12b9c4 : json2graph/decoder/decode_obj_package.py
# region: set_package_containsmodelelement_modelelement (lines 60-87, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef
import ontouml_shim as args
from ontouml_shim import ontouml_ref, get_package_contents

def set_package_containsmodelelement_modelelement(package_dict: dict, ontouml_graph: Graph) -> None:
    """Set object property ontouml:containsModelElement between an ontouml:Package and an ontouml:ModelElement it \
    contains.

    :param package_dict: Package's data to have its fields decoded.
    :type package_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """
    # Get the list inside the 'contents' key
    # Include found related elements in graph using ontouml:containsModelElement
    for content in get_package_contents(package_dict, package_dict["id"]):
        ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + package_dict["id"]),
                           ontouml_ref("containsModelElement"),
                           URIRef(args.ARGUMENTS["base_uri"] + content["id"])))

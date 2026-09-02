# Context shim (see meta.json): subset of json2graph/modules/arguments.py
# (the ARGUMENTS dict), json2graph/modules/utils_graph.py (ontouml_ref), and
# json2graph/decoder/decode_obj_package.py's own get_package_contents --
# defined just above this region in the same source file, not part of the
# captured context lines -- from OntoUML/ontouml-json2graph@982f12b9c4, so
# the region executes outside the package. get_package_contents is copied
# verbatim (self-contained: no import beyond dict/list built-ins).
# Identical bindings for both representations.
from rdflib import URIRef

ARGUMENTS = {"base_uri": "https://example.org#"}


def ontouml_ref(entity: str) -> URIRef:
    return URIRef("https://w3id.org/ontouml#" + entity)


def get_package_contents(package_dict: dict, package_id: str, list_contents: list = []) -> list:
    """Receive the dictionary with all loaded JSON data and returns the value of the 'contents' field for a given \
    object (defined by the received value of its ID).
    """
    # End of recursion
    if package_dict["id"] == package_id:
        if "contents" in package_dict:
            list_contents = package_dict["contents"].copy()
        else:
            list_contents = []

    # Recursively treats sub-dictionaries
    else:
        if list_contents:
            return list_contents

        for key in package_dict.keys():
            # Treat case dictionary
            if type(package_dict[key]) is dict:
                list_contents = get_package_contents(package_dict[key], package_id)

            # Treat case list
            elif type(package_dict[key]) is list:
                for item in package_dict[key]:
                    if type(item) is dict:
                        list_contents = get_package_contents(item, package_id, list_contents)

                    if list_contents:
                        break

    return list_contents

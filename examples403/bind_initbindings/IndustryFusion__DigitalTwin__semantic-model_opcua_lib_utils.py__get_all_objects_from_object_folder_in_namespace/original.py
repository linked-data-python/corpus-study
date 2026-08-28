# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/lib/utils.py
# region: get_all_objects_from_object_folder_in_namespace (lines 450-472, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib import URIRef, Namespace, Graph, Literal, BNode

def get_all_objects_from_object_folder_in_namespace(g, namespace, basens, opcuans):
    """Derives all opcua objects in a namespace

    Args:
        g (RDF Graph): graph to search in
        namespace (RDFURIRef): namespace to search in
    """
    query = """
    SELECT ?object WHERE {{
        BIND(<{namespace}> as ?namespace)
        opcua:nodei85 opcua:Organizes ?object .
        FILTER(
            STRSTARTS(STR(?object), STR(?namespace)) &&
                !REGEX(
                SUBSTR(STR(?object), STRLEN(STR(?namespace)) + 1),
                  "[/#]"
            )
        )
    }}
    """.format(namespace=namespace)
    result = g.query(query, initNs={'base': basens, 'opcua': opcuans})
    # Transform result in list of URIRefs
    return [URIRef(str(r['object'])) for r in result]

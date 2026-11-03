# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/dataservice/tests/server/binding_server.py
# region: parse_rdf_to_mapping (lines 141-200, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib import RDF, Graph, Namespace
import re
import sys
LocalizedText = None
opcua_ns = Namespace('http://opcfoundation.org/UA/')

def parse_rdf_to_mapping(rdf_file, base_ns, binding_ns=None, uaentity_ns=None):
    g = Graph().parse(rdf_file, format="turtle")

    # Define the base namespace for the vocabulary
    BASE = Namespace(base_ns)

    # Check for binding and UA entity namespaces in RDF
    if not (binding_ns or g.namespace_manager.store.namespace("binding")):
        print("Error: Binding namespace not found in RDF data, and no binding namespace provided.")
        sys.exit(1)
    if not (uaentity_ns or g.namespace_manager.store.namespace("uaentity")):
        print("Error: UA entity namespace not found in RDF data, and no UA entity namespace provided.")
        sys.exit(1)

    nsu_pattern = re.compile(r'nsu=(.*?);i=(\d+)')

    # Translate RDF Datatype to Python Type
    python_types = {
        opcua_ns.Double: float,
        opcua_ns.Boolean: bool,
        opcua_ns.Int32: int,
        opcua_ns.String: str,
        opcua_ns.LocalizedText: LocalizedText,
    }

    mapping_data = {}
    for s in g.subjects(RDF.type, BASE.BoundMap):
        connector_attribute = g.value(s, BASE.bindsConnectorParameter)
        datatype_uri = g.value(s, BASE.bindsMapDatatype)

        if connector_attribute and datatype_uri:
            # Parse namespace and identifier from connector_attribute
            match = nsu_pattern.match(str(connector_attribute))
            if match:
                namespace_uri = match.group(1)
                node_id = f"i={match.group(2)}"
            else:
                namespace_uri = None
                node_id = str(connector_attribute)

            if datatype_uri not in python_types:
                print(f"Warning, could not determine python type for {datatype_uri}. Using default: str.")
            datatype = python_types.get(datatype_uri, str)  # Default to string if not recognized

            mapping_data[node_id] = {'namespace': namespace_uri, 'datatype': datatype}

    return mapping_data

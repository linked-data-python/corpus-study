# Extracted from neo4j-labs/rdflib-neo4j@47fcfc080e : rdflib_neo4j/config/Neo4jStoreConfig.py
# region: Neo4jStoreConfig.set_custom_prefix (lines 115-128, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib import Namespace, URIRef

def set_custom_prefix(self, name: str, value: str):
    """
    Add a custom prefix to the configuration.

    Parameters:
    - name: The name of the prefix.
    - value: The value of the prefix (namespace URI).

    Raises:
    - Exception: If the namespace is already defined for another prefix.
    """
    if Namespace(value) in self.custom_prefixes.values():
        raise Exception(f"Namespace {value} already defined for another prefix.")
    self.custom_prefixes[name] = Namespace(value)

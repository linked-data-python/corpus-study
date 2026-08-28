# Extracted from philbarker/TAP2SHACL@910ab540e2 : src/ap2shacl/ap2shaclConverter.py
# region: AP2SHACLConverter.convert_namespaces (lines 151-158, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, Literal, BNode, Namespace

def convert_namespaces(self):
    """Bind the namespaces in the application profle to the SHACL graph."""
    for prefix in self.ap.namespaces.keys():
        ns_uri = URIRef(self.ap.namespaces[prefix])
        ns = Namespace(ns_uri)
        self.sg.bind(prefix, ns)
        if "base" == prefix.lower():
            self.sg.base = ns_uri

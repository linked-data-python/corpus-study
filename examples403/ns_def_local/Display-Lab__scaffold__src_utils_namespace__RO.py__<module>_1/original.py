# Extracted from Display-Lab/scaffold@d368cfe17c : src/utils/namespace/_RO.py
# region: <module> (lines 1-16, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib import Namespace, URIRef

from src.utils.namespace import AliasingDefinedNamespace


class RO(AliasingDefinedNamespace):
    _NS = Namespace("http://purl.obolibrary.org/obo/")

    # http://www.w3.org/1999/02/22-rdf-syntax-ns#Property

    RO_0000091: URIRef
    has_disposition: URIRef

    _alias = {
        "has_disposition": "RO_0000091",
    }

# Extracted from BD2KOnFHIR/fhirtordf@05b23ba1df : fhirtordf/rdfsupport/fhirgraphutils.py
# region: extension (lines 31-40, stratum trav_navigation)
# licence of the source repository: see meta.json
from datetime import datetime, date
from typing import Union, Optional, Tuple, List
from rdflib import Graph, BNode, Literal, RDF
from rdflib.term import Identifier, URIRef, Node
from fhirtordf.rdfsupport.namespaces import FHIR

def extension(g: Graph, node: Identifier, extension_predicate: Union[URIRef, str], asLiteral=False) -> \
        Union[None, BNode, date, bool, datetime, int, float]:
    ext_pred = str(extension_predicate)
    for ext in g.objects(node, FHIR.Element.extension):
        if value(g, ext, FHIR.Extension.url) == ext_pred:
            for p, o in g.predicate_objects(ext):
                # TODO: Think this through -- do we need something in the RDF
                if 'Extension.value' in str(p):
                    return value(g, ext, p, asLiteral)
    return None

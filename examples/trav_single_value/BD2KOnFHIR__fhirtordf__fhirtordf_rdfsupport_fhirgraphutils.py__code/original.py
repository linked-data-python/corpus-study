# Extracted from BD2KOnFHIR/fhirtordf@05b23ba1df : fhirtordf/rdfsupport/fhirgraphutils.py
# region: code (lines 43-50, stratum trav_single_value)
# licence of the source repository: see meta.json
from typing import Union, Optional, Tuple, List
from rdflib import Graph, BNode, Literal, RDF
from rdflib.term import Identifier, URIRef, Node
from fhirtordf.rdfsupport.namespaces import FHIR

def code(g: Graph, subject: Node, predicate: URIRef, system: Optional[Union[URIRef, str]]=None,
         asLiteral: bool=False) -> Union[Node, str, None]:
    c = g.value(subject, predicate)
    if c:
        for coding in g.objects(c, FHIR.CodeableConcept.coding):
            if not system or str(system) == value(g, coding, FHIR.Coding.system):
                return value(g, coding, FHIR.Coding.code, asLiteral=asLiteral)
    return None

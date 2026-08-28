# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: Property.__repr__.canonicalName (lines 2017-2029, band medium)
# licence of the source repository: see meta.json
from rdflib import (
    BNode,
    Literal,
    Namespace,
    RDF,
    RDFS,
    URIRef,
    Variable
)
from rdflib.namespace import XSD as _XSD_NS
from rdflib.util import first
OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

def canonicalName(term, g):
    normalizedName = classOrIdentifier(term)
    if isinstance(normalizedName, BNode):
        return term
    elif normalizedName.startswith(_XSD_NS):
        return str(term)
    elif first(g.triples_choices((
                                 normalizedName,
                                 [OWL_NS.unionOf,
               OWL_NS.intersectionOf], None))):
        return repr(term)
    else:
        return str(term.qname)

# Extracted from weblyzard/ewrt@14a2bc26a1 : src/eWRT/input/conv/cxl/__init__.py
# region: XCL2RDF._addOntologyStatement (lines 62-80, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import Namespace, Literal
NS_WL   = Namespace("http://www.weblyzard.com/2005/03/31/wl#")
NS_RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")

@staticmethod
def _addOntologyStatement( ontology, s, p, o ):
    """ adds the given statement to the ontology using the
        wl-syntax 
    """
    # ignore statements with empty s, p, or o.
    if not p or not s or not o:
        return

    # returns the resource's identifier
    rid = lambda r: NS_WL[ XCL2RDF._getIdentifier(r)] 

    # define labels
    ontology.add( (rid(s), NS_RDFS['label'], Literal(s)) )
    ontology.add( (rid(o), NS_RDFS['label'], Literal(o)) )
    ontology.add( (rid(p), NS_RDFS['label'], Literal(p)) )

    # add relation(
    ontology.add( (rid(s), rid(p), rid(o)) )

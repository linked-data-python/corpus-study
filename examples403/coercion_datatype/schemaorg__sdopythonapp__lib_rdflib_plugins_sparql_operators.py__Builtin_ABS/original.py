# Extracted from schemaorg/sdopythonapp@128be97d35 : lib/rdflib/plugins/sparql/operators.py
# region: Builtin_ABS (lines 92-97, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import URIRef, BNode, Variable, Literal, XSD, RDF

def Builtin_ABS(expr, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-abs
    """

    return Literal(abs(numeric(expr.arg)))

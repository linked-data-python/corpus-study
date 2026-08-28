# Extracted from LexMalta/recipes@b861b7ccea : recipe-importer/rdflib/plugins/sparql/operators.py
# region: Builtin_STRSTARTS (lines 318-327, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import RDF, XSD, BNode, Literal, URIRef, Variable

def Builtin_STRSTARTS(expr, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-strstarts
    """

    a = expr.arg1
    b = expr.arg2
    _compatibleStrings(a, b)

    return Literal(a.startswith(b))

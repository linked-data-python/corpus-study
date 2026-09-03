# Context shim (see meta.json): subset of
# recipe-importer/rdflib/plugins/sparql/operators.py from
# LexMalta/recipes@b861b7ccea (itself a vendored, unmodified copy of
# rdflib.plugins.sparql.operators from upstream rdflib) -- restores the two
# helpers Builtin_STRSTARTS calls but that live outside the extracted lines
# (309-315 and 1017-1026 of the same file), so the region executes
# standalone. Identical bindings for both representations.
from rdflib import XSD, Literal
from rdflib.plugins.sparql.sparql import SPARQLError


def string(s):
    """Make sure the passed thing is a string literal.

    i.e. plain literal, xsd:string literal or lang-tagged literal
    """
    if not isinstance(s, Literal):
        raise SPARQLError("Non-literal passes as string: %r" % s)
    if s.datatype and s.datatype != XSD.string:
        raise SPARQLError("Non-string datatype-literal passes as string: %r" % s)
    return s


def _compatibleStrings(a, b):
    string(a)
    string(b)

    if b.language and a.language != b.language:
        raise SPARQLError("incompatible arguments to str functions")

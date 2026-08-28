# Context shim (see meta.json): the region is a method of infixowl's Class, in
# rdflib/extras/infixowl.py of MKLab-ITI/prophet@eee2ab51de -- a vendored copy
# of a python-2 era rdflib (it starts with `from rdflib import py3compat`), so
# the module cannot be imported against the rdflib 7 of this environment, and
# the modern rdflib.extras.infixowl is a different, rewritten module.
# This shim therefore carries the one helper the region calls, verbatim from
# that file (lines 237-243), plus the two marker classes its isinstance test
# needs.  Imported identically by original.py and translated.ldpy.
from rdflib import BNode, URIRef


class Property:
    """Marker stand-in: only classOrIdentifier's isinstance test uses it."""

    def __init__(self, identifier):
        self.identifier = identifier


class Class:
    """Marker stand-in: only classOrIdentifier's isinstance test uses it."""

    def __init__(self, identifier):
        self.identifier = identifier


# verbatim from rdflib/extras/infixowl.py lines 237-243
def classOrIdentifier(thing):
    if isinstance(thing, (Property, Class)):
        return thing.identifier
    else:
        assert isinstance(thing, (URIRef, BNode)), \
            "Expecting a Class, Property, URIRef, or BNode.. not a %s" % thing
        return thing

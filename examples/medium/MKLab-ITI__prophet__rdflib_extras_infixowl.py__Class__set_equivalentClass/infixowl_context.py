# Context shim (see meta.json): the bindings the region needs from
# rdflib/extras/infixowl.py at MKLab-ITI/prophet@eee2ab51de.  The module
# itself cannot be imported here: its first statement is
# `from rdflib import py3compat`, a helper dropped from rdflib long ago.
# Used IDENTICALLY by original.py and translated.ldpy.
from rdflib import BNode, URIRef


class Property:
    """Placeholder for infixowl.Property, reduced to the single attribute
    `classOrIdentifier` reads.  The real class is an AnnotatableTerms
    subclass of ~400 lines; only `identifier` is relevant here."""

    def __init__(self, identifier):
        self.identifier = identifier

    def __eq__(self, other):
        # value equality so that the driver can compare the arguments it
        # handed to each side; the region itself never compares these.
        return type(self) is type(other) and self.identifier == other.identifier


class Class(Property):
    """Placeholder for infixowl.Class — see Property above."""


def classOrIdentifier(thing):
    # verbatim, rdflib/extras/infixowl.py lines 237-243
    if isinstance(thing, (Property, Class)):
        return thing.identifier
    else:
        assert isinstance(thing, (URIRef, BNode)), \
            "Expecting a Class, Property, URIRef, or BNode.. not a %s" % thing
        return thing

# Context shim (see meta.json): the region is CastClass from
# rdflib/extras/infixowl.py of MKLab-ITI/prophet@eee2ab51de -- a vendored copy
# of a python-2 era rdflib (it starts with `from rdflib import py3compat`), so
# the module cannot be imported against the rdflib 7 of this environment, and
# the modern rdflib.extras.infixowl is a different, rewritten module.
#
# Copied verbatim from that file:
#   * classOrIdentifier                (lines 237-243)
#   * MalformedClass                   (lines 842-847)
#   * Restriction.restrictionKinds     (lines 1604-1608)
# The four class collaborators CastClass may return (Restriction, BooleanClass,
# EnumeratedClass, Class) are constructor-recording stand-ins: the region only
# ever *constructs* them, and their real bodies are hundreds of lines of
# python-2 rdflib.  Two stand-ins compare equal when they were built from the
# same arguments (graphs compared by isomorphism), which is exactly what the
# harness needs to see.  Imported identically by original.py and
# translated.ldpy.
from rdflib import BNode, Graph, Namespace, URIRef
from rdflib.compare import to_isomorphic

OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")


def _key(value):
    if isinstance(value, Graph):
        return ("graph", to_isomorphic(value).graph_digest())
    if isinstance(value, BNode):
        return ("bnode",)
    if isinstance(value, dict):
        return tuple(sorted((k, _key(v)) for k, v in value.items()))
    if isinstance(value, (list, tuple)):
        return tuple(_key(v) for v in value)
    return value


class _Recorded:
    """Records the constructor call; equal iff built the same way."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    @property
    def identifier(self):
        if self.args:
            return self.args[0]
        return self.kwargs.get("identifier")

    def __eq__(self, other):
        return (type(self) is type(other)
                and _key(self.args) == _key(other.args)
                and _key(self.kwargs) == _key(other.kwargs))

    def __repr__(self):
        return f"{type(self).__name__}(*{self.args!r}, **{self.kwargs!r})"


class Property(_Recorded):
    """Marker stand-in: only classOrIdentifier's isinstance test uses it."""


class Class(_Recorded):
    """Stand-in; also the isinstance marker used by classOrIdentifier."""


class Restriction(_Recorded):
    # verbatim from rdflib/extras/infixowl.py lines 1604-1608
    restrictionKinds = [OWL_NS.allValuesFrom,
                        OWL_NS.someValuesFrom,
                        OWL_NS.hasValue,
                        OWL_NS.maxCardinality,
                        OWL_NS.minCardinality]


class EnumeratedClass(_Recorded):
    """Stand-in."""


class BooleanClass(_Recorded):
    """Stand-in."""


# verbatim from rdflib/extras/infixowl.py lines 842-847
class MalformedClass(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __repr__(self):
        return self.msg


# verbatim from rdflib/extras/infixowl.py lines 237-243
def classOrIdentifier(thing):
    if isinstance(thing, (Property, Class)):
        return thing.identifier
    else:
        assert isinstance(thing, (URIRef, BNode)), \
            "Expecting a Class, Property, URIRef, or BNode.. not a %s" % thing
        return thing

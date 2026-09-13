# Context shim (see meta.json): subset of usc-isi-i2/etk@2084003ae7, so the
# region executes outside the package (etk is not installed here).
# Identical bindings/behaviour for both representations.
#
# etk/knowledge_graph/node.py: Node/URI/BNode copied verbatim -- the region
# under test (SHACLOntoConverter.cnode) only ever produces/compares these
# two. Literal is copied verbatim too (it is imported by the region's own
# context line, even though test_cnode never constructs one). LiteralType is
# a minimal stand-in: the real class (same file) is a ~130-line regex-based
# xsd/rdf datatype validator, none of which test_cnode reaches -- only its
# identity as a URI subclass matters here, so it is stubbed to that.
#
# etk/knowledge_graph/graph.py: Graph is stubbed to the one thing
# SHACLOntoConverter.__init__ calls on it, `.bind(prefix, namespace)` -- the
# real class wraps an rdflib.Graph store, not otherwise reached by cnode().
#
# etk/knowledge_graph/shacl.py: SH (a plain Namespace, imported by the
# region's own context line but not used inside test_cnode's body) and
# SHACLOntoConverter.__init__/.cnode/.class_nodes, copied verbatim. SHACL
# (also imported, also unused inside this region) is a stand-in: the real
# class wraps pyshacl validation, not installed here and not reached.
from uuid import uuid4


class InvalidGraphNodeValueError(Exception):
    pass


class UnknownLiteralType(Exception):
    pass


class Node(object):
    def __init__(self, value):
        if not isinstance(value, str):
            raise InvalidGraphNodeValueError()
        self._value = value

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self._value == other._value

    def __hash__(self):
        return hash(self.value)

    @property
    def value(self):
        return self._value

    def is_valid(self):
        raise NotImplementedError('Subclass should implement this.')


class URI(Node):
    def __init__(self, value):
        if isinstance(value, URI):
            super().__init__(value.value)
        else:
            super().__init__(value)

    def __eq__(self, other):
        if not isinstance(other, URI):
            return False
        return super().__eq__(other)

    def __hash__(self):
        return hash(self.value)

    def is_valid(self):
        return self.value is not None


class BNode(Node):
    def __init__(self, value=None):
        if isinstance(value, BNode):
            super().__init__(value.value)
        else:
            if not value:
                value = uuid4().hex
            super().__init__(value)

    def __eq__(self, other):
        if not isinstance(other, BNode):
            return False
        return super().__eq__(other)

    def __hash__(self):
        return hash(self.value)

    def is_valid(self):
        return self.value is not None


class Literal(Node):
    def __init__(self, value, lang=None, type_=None):
        if isinstance(value, Literal):
            super().__init__(value.value)
            self._lang = value.lang
            self._type = value._type
        else:
            super().__init__(value)
            self._lang = lang
            if type_ and isinstance(type_, str):
                type_ = LiteralType(type_)
            self._type = type_

    def __eq__(self, other):
        if not isinstance(other, Literal):
            return False
        return super().__eq__(other) and self.lang == other.lang and self.type == other.type

    def __hash__(self):
        return hash((self.value, self.lang, self.raw_type))

    @property
    def lang(self):
        return self._lang

    @property
    def type(self):
        return self._type

    @property
    def raw_type(self):
        if self._type:
            return self._type.value


class LiteralType(URI):
    """Stub: not exercised by test_cnode, see module docstring above."""
    def __init__(self, s, common_check=True):
        self.common_check = common_check
        self._type = None
        super().__init__(s)


class Graph:
    """Stub: only .bind() is called from SHACLOntoConverter.__init__, and
    test_cnode never inspects it."""
    def bind(self, prefix, namespace):
        pass


from rdflib import Namespace

SH = Namespace('http://www.w3.org/ns/shacl#')


class SHACL:
    """Stub: pyshacl-backed real class, not reached by test_cnode."""
    pass


from typing import Dict, Union


class SHACLOntoConverter:
    def __init__(self, class_nodes: Dict[str, Union[URI, BNode]] = None):
        super().__init__()
        self.onto_graph = None
        self._g = Graph()
        self._class_nodes = class_nodes if class_nodes else {}
        self._g.bind('sh', SH)

    def cnode(self, class_):
        class_ = str(class_)
        if class_ not in self._class_nodes:
            self._class_nodes[class_] = BNode()
        return self._class_nodes[class_]

    @property
    def class_nodes(self):
        return self._class_nodes

# Context shim (see meta.json): the part of usc-isi-i2/kgtk@b8d946b423 that the
# region reaches through `self` and through its imports, so it executes outside
# the kgtk package (which is not installed in the study venv). Identical
# bindings for both representations.
#
#  - node classes             kgtk/knowledge_graph/node.py, verbatim except that
#                             BNode() draws its id from a counter instead of
#                             uuid4(), so that two runs of the same program
#                             mint the same ids (the two sides are compared)
#  - Subject                  kgtk/knowledge_graph/subject.py (add_property
#                             without the `reify` option, which the region never
#                             uses)
#  - Graph                    kgtk/knowledge_graph/graph.py, reduced to
#                             bind / add_subject / URI resolution
#  - SHACLOntoConverter       kgtk/knowledge_graph/shacl.py, verbatim, WITHOUT
#                             _convert_ontology_owl_restriction (the region) nor
#                             the other conversions
import itertools
import re
from datetime import datetime
from typing import Dict, Union

import rdflib
from rdflib import RDF, RDFS, XSD, Namespace

_BNODE_COUNTER = itertools.count(1)


class InvalidGraphNodeValueError(Exception):
    pass


class UnknownLiteralType(Exception):
    pass


class InvalidParameter(Exception):
    pass


SH = Namespace('http://www.w3.org/ns/shacl#')

from datetime import datetime
import re


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
                value = "b%d" % next(_BNODE_COUNTER)
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

    def __str__(self):
        return self.value

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

    def is_valid(self):
        if self.value is None:
            return False
        if self._type == LiteralType.string and not self._lang:
            return False
        return self._type.is_value_valid(self.value)


class __Type(type):
    def __getattr__(self, item):
        return LiteralType(item)


class LiteralType(URI, metaclass=__Type):
    valid_time_pattern = re.compile(
        r"[\-]?(\d{4})-((0[1-9])|(1[0-2]))-(0[1-9]|[12][0-9]|3[01])T(0[0-9]|1[0-9]|2[0-3])"
        r":(0[0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9]):(0[0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])")
    valid_month_pattern = re.compile(r"[\-]?(\d{4})-((0[1-9])|(1[0-2]))-(00)T00:00:00")
    valid_year_decade_millennium_pattern = re.compile(r"[\-]?(\d{4})-(00)-(00)T00:00:00")
    valid_hundred_thousand_years_pattern = re.compile(r"[\-]?(\d{6,7})-(0[0|1])-(0[0|1])T00:00:00")
    valid_million_billion_years = re.compile(r"[\-]?(\d{8}\d+)-(0[0|1])-(0[0|1])T00:00:00")

    def __init__(self, s, common_check=True):
        self.common_check = common_check
        self._type = None
        super().__init__(self._resolve(s))

    def _resolve(self, s):
        if not isinstance(s, str):
            raise UnknownLiteralType()
        if not self.common_check:
            return s
        # complete xsd uri
        if s.startswith(self.xsd) and s[len(self.xsd):] in self.xsd_tokens:
            self._type = s[len(self.xsd):]
            return s
        # complete rdf uri
        elif s.startswith(self.rdf) and s[len(self.rdf)] in self.rdf_tokens:
            self._type = s[len(self.rdf)]
            return s
        # xsd prefix
        elif s.startswith('xsd:'):
            s = s[4:]
            if s in self.xsd_tokens:
                self._type = s
                return self.xsd + s
        # rdf prefix
        elif s.startswith('rdf:'):
            s = s[4:]
            if s in self.rdf_tokens:
                self._type = s
                return self.rdf + s
        # no prefix
        elif self._is_valid_field(s):
            if s in self.xsd_tokens:
                self._type = s
                return self.xsd + s
            elif s in self.rdf_tokens:
                self._type = s
                return self.rdf + s
        raise UnknownLiteralType()

    def _is_valid_field(self, s):
        return s in self.xsd_tokens or s in self.rdf_tokens

    def is_value_valid(self, s):
        """
        If value `s` if valid in current LiteralType
        """
        if self._type in self.value_validator:
            return self.value_validator[self._type](s)

        return True

    @staticmethod
    def _is_valid_date_time(s):

        if isinstance(s, datetime):
            return True

        try:
            # python 3.7
            datetime.fromisoformat(s)
            return True
        except Exception:
            pass

        valid_format = [
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f%z'
        ]
        try:
            for f in valid_format:
                datetime.strptime(s, f)
                return True
        except Exception:
            pass

        validity_list = [LiteralType.valid_time_pattern.match(s),
                         LiteralType.valid_month_pattern.match(s),
                         LiteralType.valid_year_decade_millennium_pattern.match(s),
                         LiteralType.valid_hundred_thousand_years_pattern.match(s),
                         LiteralType.valid_million_billion_years.match(s)]
        return any(validity_list)

    xsd = 'http://www.w3.org/2001/XMLSchema#'
    rdf = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
    xsd_tokens = {
        'time', 'date', 'dateTime', 'string', 'normalizedString', 'token', 'language', 'boolean', 'decimal', 'integer',
        'nonPositiveInteger', 'long', 'nonNegativeInteger', 'negativeInteger', 'int', 'unsignedLong', 'positiveInteger',
        'short', 'unsignedInt', 'byte', 'unsignedShort', 'unsignedByte', 'float', 'double', 'base64Binary', 'anyURI'
    }
    rdf_tokens = {'XMLLiteral', 'HTML'}
    value_validator = {
        'dateTime': _is_valid_date_time.__func__,
    }


class Subject:
    def __init__(self, s):
        if not isinstance(s, (URI, BNode)):
            raise InvalidParameter('Subject needs to be URI or BNode')
        self._resource = dict()
        self._s = s

    def add_property(self, p, o, reify=None):
        if not isinstance(p, URI):
            raise InvalidParameter('Predict needs to be URI')
        if not self.__is_valid_object(o):
            raise InvalidParameter('Object needs to be URI or BNode or Literal or Triple')

        if p not in self._resource:
            self._resource[p] = set([])
        self._resource[p].add(o)

    @property
    def subject(self):
        return self._s

    @staticmethod
    def __is_valid_object(o):
        return isinstance(o, (URI, BNode, Literal, Subject))

    def __iter__(self):
        for p, os in self._resource.items():
            for o in os:
                yield self._s, p, o


URI_PATTERN = re.compile(r'^http:|^urn:|^info:|^ftp:|^https:')


class Graph(object):
    def __init__(self, graph=None, identifier=None):
        if graph:
            self._g = graph
        else:
            self._g = rdflib.Graph(identifier=identifier)

    def bind(self, prefix, namespace, override=True, replace=False):
        self._g.bind(prefix, namespace, override, replace)

    def add_subject(self, subjects, context=None):
        if not context:
            context = set()

        for t in subjects:
            s, p, o = t
            if isinstance(o, Subject) and o not in context:
                context.add(o)
                self.add_subject(o, context)
                o = o.subject

            # convert triple to RDFLib recognizable format
            triple = self._convert_triple_rdflib((s, p, o))
            self._g.add(triple)

    def _resolve_uri(self, uri: URI) -> rdflib.URIRef:
        text = uri.value.strip()
        if URI_PATTERN.match(text):
            return rdflib.URIRef(text)
        prefix, name = text.split(':', 1)  # prefix:name, as NamespaceManager.parse_uri
        return rdflib.URIRef(str(dict(self._g.namespaces())[prefix]) + name)

    def _convert_triple_rdflib(self, triple):
        s, p, o = triple
        sub = self._resolve_uri(s) if isinstance(s, URI) else rdflib.BNode(s.value)
        pred = self._resolve_uri(p)
        if isinstance(o, URI):
            obj = self._resolve_uri(o)
        elif isinstance(o, Subject):
            if isinstance(o.subject, URI):
                obj = self._resolve_uri(o.subject)
            else:
                obj = rdflib.BNode(o.subject.value)
        elif isinstance(o, BNode):
            obj = rdflib.BNode(o.value)
        else:
            obj = rdflib.Literal(o.value, o.lang, o.raw_type)
        return sub, pred, obj


class SHACLOntoConverter:
    def __init__(self, class_nodes: Dict[str, Union[URI, BNode]] = None):
        super().__init__()
        self.onto_graph: rdflib.Graph = None
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

    def _property_shape(self, property_: Union[rdflib.URIRef, str, URI]):
        if isinstance(property_, URI):
            property_ = property_.value
        property_ = rdflib.URIRef(property_)
        p_shape = Subject(BNode())
        p_shape.add_property(URI('sh:path'), URI(property_))
        ranges = list(self.onto_graph.objects(property_, RDFS.range))
        self._build_property_ranges(p_shape, ranges)
        return p_shape

    def _build_property_ranges(self, p_shape, ranges):
        if not ranges:
            return
        if len(ranges) == 1:
            range_ = ranges[0]
            type_ = URI('sh:datatype') if self._is_datatype(range_) else URI('sh:class')
            p_shape.add_property(type_, URI(ranges[0]))
        else:
            or_list = []
            for range_ in ranges:
                range_subject = Subject(BNode())
                type_ = URI('sh:datatype') if self._is_datatype(range_) else URI('sh:class')
                range_subject.add_property(type_, URI(range_))
                or_list.append(range_subject)
            p_shape.add_property(URI('sh:or'), self._add_list(or_list))

    @staticmethod
    def _is_datatype(uri: rdflib.URIRef):
        if isinstance(uri, rdflib.BNode):
            return False
        return uri.startswith(str(XSD)) or uri.startswith(str(RDF))

    def _class_shape(self, c):
        node_subject = Subject(self.cnode(c))
        node_subject.add_property(URI('rdf:type'), URI('sh:NodeShape'))
        node_subject.add_property(URI('sh:targetClass'), URI(c))
        return node_subject

    def _add_list(self, list_):
        """
        (:a :b :c) ===
        [ rdf:first :a ; rdf:rest [ rdf:first :b ; rdf:rest [ rdf:first :c ; rdf:rest rdf:nil]]]
        """
        if not list_:
            return URI('rdf:nil')
        head = Subject(BNode())
        head.add_property(URI('rdf:first'), list_[0])
        head.add_property(URI('rdf:rest'), self._add_list(list_[1:]))
        return head

# Context shim (see meta.json): minimal, faithful subset of rdflib_orm's
# models.py, fields.py and db/__init__.py, plus tests/__init__.py's BASE_URI,
# from edmondchuc/rdflib-orm@b278d9699b, so the region executes outside the
# package.  Identical bindings for both representations.
#
# Trimmed, nothing behaviourally changed for the five tests this region
# calls: Query/QuerySet (never reached -- .objects is not used here),
# Model.serialize(), the other Field subclasses (CharField, DateTimeField,
# BooleanField, IntegerField, RelationshipField), and the SPARQLStore
# branches of Database (set_store_header_*, sparql, sparql_update) are
# dropped.  IRIField.validate/convert/convert_to_python, Model.__init__ and
# Model.save() (rollback included) are otherwise reproduced verbatim.
#
# __namespaces__ exports BASE_URI under the prefix "base" -- this is what
# lets translated.ldpy write `from orm_context import base:` instead of
# inlining the IRI.  It works here because this module (standing in for the
# project's own tests/__init__.py) is something we can add one line to; see
# translation_notes for why the SAME trick is not available for RDF/OWL,
# which come from rdflib.namespace itself, an unmodified dependency.

import inspect
import logging
from typing import Dict

from rdflib import Graph, URIRef, Namespace

logger = logging.getLogger(__name__)

BASE_URI = Namespace('http://example.com/')
__namespaces__ = {"base": BASE_URI}


class InvalidDBKeyTypeError(Exception):
    @classmethod
    def message(cls, value):
        return f'db_key must be a str, instead it received {value} with type {type(value)}.'


class Database:
    g: Graph
    base_uri: URIRef
    databases: Dict[str, 'Database'] = {'default': None}

    def __init__(self, g: Graph, base_uri):
        self.g = g
        self.base_uri = URIRef(base_uri)
        self.is_sparql_store = False

    @classmethod
    def get_db(cls, db_key: str = 'default') -> 'Database':
        return cls.databases[db_key]

    @classmethod
    def set_db(cls, g: Graph, base_uri, db_key: str = 'default'):
        if not isinstance(db_key, str):
            raise InvalidDBKeyTypeError(InvalidDBKeyTypeError.message(db_key))
        cls.databases.update({db_key: Database(g, URIRef(base_uri))})

    def write(self, triple):
        logger.info(f'Adding triple {triple}')
        self.g.add(triple)

    def delete(self, triple):
        logger.info(f'Deleting triple {triple}')
        self.g.remove(triple)

    def read(self, triple):
        for s, p, o in self.g.triples(triple):
            logger.info(f'reading triple {(s, p, o)}')
            yield s, p, o


class FieldError(Exception):
    pass


class Field:
    def validate(self, value, cls, field):
        if self.required and value is None:
            raise FieldError(f'{cls} required field "{field}" is not set.')

    def convert(self, value, **kwargs):
        raise NotImplementedError

    def convert_to_python(self, value):
        raise NotImplementedError


class IRIField(Field):
    def __init__(self, predicate, value=None, inverse=None, required=False, many=False):
        self.predicate = predicate
        self.value = value
        self.inverse = inverse
        self.required = required
        self.many = many

    def convert(self, value, **kwargs):
        if value is None:
            return None
        if isinstance(value, str):
            if self.many is True:
                raise FieldError(f'Expected a list but got "{value}" instead.')
            if isinstance(value, Model):
                return value.__uri__
            return URIRef(value)
        if not isinstance(value, list):
            raise FieldError('Expected a list.')
        result = []
        for item in value:
            if isinstance(item, Model):
                result.append(item.__uri__)
            else:
                result.append(URIRef(item))
        return result

    def convert_to_python(self, value):
        if self.many:
            if isinstance(value, Model):
                return [str(value.__uri__)]
            return [str(value)]
        if isinstance(value, Model):
            return str(value.__uri__)
        return str(value)


class ModelBase(type):
    def __new__(mcs, name, bases, attrs, **kwargs):
        new_class = super().__new__(mcs, name, bases, attrs)
        if new_class.Meta.mixin is False and new_class.__name__ not in ('ModelBase', 'Model'):
            assert hasattr(new_class, 'class_type'), f'{new_class} must have the attribute class_type.'
            assert isinstance(getattr(new_class, 'class_type'), IRIField), \
                f'{new_class} must be an instance of IRIField.'
        return new_class


class Model(metaclass=ModelBase):
    class_type = None

    class Meta:
        mixin = False

    def __eq__(self, other):
        if isinstance(other, Model):
            return self.__uri__ == other.__uri__
        raise NotImplementedError()

    def __hash__(self):
        return hash(self.__uri__)

    @staticmethod
    def get_model_attributes(cls):
        return list(filter(
            lambda kv: not kv[0].startswith('__')
            and not inspect.ismethod(kv[1])
            and kv[0] not in ('objects', 'get_model_attributes', 'save', 'Meta', 'serialize'),
            inspect.getmembers(cls),
        ))

    def __init__(self, uri: str, db_key: str = 'default', **kwargs):
        cls = self.__class__
        db = Database.get_db(db_key)
        if not uri:
            raise Exception(f'{cls} instance uri is an empty string.')
        if not uri.startswith('http'):
            self.__uri__ = URIRef(db.base_uri + uri)
        else:
            self.__uri__ = URIRef(uri)
        self.__attributes__ = self.get_model_attributes(self)
        for attribute_name, attribute_field in self.__attributes__:
            if kwargs.get(attribute_name) is not None:
                value = kwargs[attribute_name]
            else:
                value = attribute_field.value
            attribute_field.validate(value, cls, attribute_name)
            setattr(self, attribute_name, value)

    def save(self, db_key: str = 'default'):
        uri = self.__uri__
        cls = self.__class__
        db = Database.get_db(db_key)

        previous_state = Graph()
        for _, p, o in db.read((uri, None, None)):
            previous_state.add((uri, p, o))

        def delete_current_triples(uri):
            g = Database.get_db(db_key)
            for _, p, o in g.read((uri, None, None)):
                g.delete((uri, p, o))
            for s, p, _ in g.read((None, None, uri)):
                g.delete((s, p, uri))

        delete_current_triples(uri)

        try:
            for attribute_name, attribute_field in self.__attributes__:
                predicate = attribute_field.predicate
                inverse = getattr(attribute_field, 'inverse', None)
                value = getattr(self, attribute_name)

                attribute_field.validate(value, cls, attribute_name)
                converted_value = attribute_field.convert(value)

                if converted_value is not None:
                    if isinstance(converted_value, list):
                        for item in converted_value:
                            db.write((uri, predicate, item))
                            if inverse is not None:
                                db.write((item, inverse, uri))
                    else:
                        db.write((uri, predicate, converted_value))
                        if inverse is not None:
                            db.write((converted_value, inverse, uri))
        except Exception as e:
            logger.info('Rolling back transaction')
            delete_current_triples(uri)
            for s, p, o in previous_state.triples((None, None, None)):
                db.write((s, p, o))
            raise e


import types as _types
models = _types.SimpleNamespace(Model=Model, IRIField=IRIField, FieldError=FieldError)

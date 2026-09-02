# Context shim (see meta.json), for
# DataArtifex/rdf-toolkit@226d8a1be33a80222970db6264a5e35f261bc16c,
# src/dartfx/rdf/pydantic/_base.py.
#
# `_serialise_into_graph` is a method of `RdfBaseModel`, extracted with an
# explicit `self` parameter. Everything it reaches through `self` --
# `self._subject_uri`, `self._bind_prefixes`, `self.rdf_type`,
# `self.__class__.model_fields`, `self._value_to_node` -- is outside the
# extracted region (lines 1335-1409) and is restored here. Two groups of
# bindings, treated differently:
#
#   - `_bind_prefixes` and `_value_to_node` (lines 1484-1560 of the real
#     file) are copied VERBATIM from the pinned commit, because the region
#     calls them directly and their exact branching (LangString/bytes/Enum/
#     datetime/... dispatch) is part of what the pair must agree on. Same
#     for the free functions they in turn call: `_get_rdf_property`,
#     `_field_type_info` (+ its helpers `_unwrap_annotation`/
#     `_annotation_metadata`), `_python_datatype`, `_ensure_uri`,
#     `_looks_like_uri`, `_default_prefixes`.
#   - `RdfProperty` is copied verbatim too (it is a plain frozen dataclass in
#     the real source, lines 496-... -- docstrings trimmed here).
#   - `LangString`/`LangStringList` are NOT the real Pydantic-`BaseModel`-
#     based classes (the real ones pull in the full `_coerce_to_lang_string_list`
#     validation machinery that this region never calls): they are reduced to
#     plain dataclasses/list-subclass carrying only `.value`/`.lang`, which is
#     all `_value_to_node`'s `isinstance(value, LangStringList)` fast path and
#     the `isinstance(value, LangString)` branch inside `_value_to_node`
#     actually read.
#   - `RdfBaseModelStub` replaces `RdfBaseModel` itself: real `RdfBaseModel`
#     is a full Pydantic `BaseModel` with a `rdf_uri_generator` field,
#     `model_fields` built by Pydantic's metaclass, etc. The region under
#     test never constructs a model through Pydantic -- it only calls
#     `self._subject_uri(...)`, `self._bind_prefixes(graph)`,
#     `self.__class__.model_fields`, `self._value_to_node(...)` and reads
#     `self.rdf_type` -- so the stub supplies those as plain attributes/
#     methods, with `_subject_uri` simplified to return a fixed URIRef
#     (real `_subject_uri` delegates to a UUID/BNode-minting
#     `RdfUriGenerator` that this region does not exercise: it only calls
#     the method and uses whatever it returns as the subject).
#
# Identical bindings for both representations.
from __future__ import annotations

import uuid
from dataclasses import dataclass, field as dc_field
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from types import SimpleNamespace
from typing import Any, Union, get_args, get_origin

from rdflib import RDF, XSD, BNode, Graph, Literal, Namespace, URIRef


# --- LangString / LangStringList: minimal stand-ins (see header) ----------

@dataclass
class LangString:
    value: str
    lang: str | None = None


class LangStringList(list):
    """Same role as the real LangStringList: a list of LangString."""


# --- RdfProperty: copied verbatim (dataclass shape + predicate_uri/datatype_uri) ---

@dataclass(frozen=True)
class RdfProperty:
    predicate: str | URIRef
    datatype: str | URIRef | None = None
    language: str | None = None
    serializer: Any | None = None
    parser: Any | None = None

    def predicate_uri(self) -> URIRef:
        result = _ensure_uri(self.predicate)
        assert result is not None
        return result

    def datatype_uri(self) -> URIRef | None:
        return _ensure_uri(self.datatype)


# --- free functions: copied verbatim from _base.py (see header) -----------

def _ensure_uri(value):
    if value is None:
        return None
    if isinstance(value, URIRef):
        return value
    if isinstance(value, Namespace):
        return URIRef(str(value))
    return URIRef(str(value))


import re
URI_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def _looks_like_uri(value: str) -> bool:
    return bool(URI_PATTERN.match(value))


def _default_prefixes() -> dict[str, str]:
    return {"rdf": str(RDF), "xsd": str(XSD)}


def _python_datatype(value):
    if isinstance(value, bool):
        return XSD.boolean
    if isinstance(value, int):
        return XSD.integer
    if isinstance(value, float):
        return XSD.double
    if isinstance(value, datetime):
        return XSD.dateTime
    if isinstance(value, date):
        return XSD.date
    if isinstance(value, time):
        return XSD.time
    if isinstance(value, Decimal):
        return XSD.decimal
    if isinstance(value, bytes):
        return XSD.base64Binary
    if isinstance(value, uuid.UUID):
        return XSD.string
    return None


def _unwrap_annotation(annotation):
    while True:
        origin = get_origin(annotation)
        if origin is None:
            return annotation
        # real code also unwraps typing.Annotated here; our test fields
        # never use Annotated (RdfProperty travels via field.metadata
        # directly, see FieldInfo below), so that branch is not reached.
        return annotation


def _get_rdf_property(field):
    metadata = getattr(field, "metadata", ()) or ()
    for item in metadata:
        if isinstance(item, RdfProperty):
            return item
    return None


def _field_type_info(field):
    annotation = getattr(field, "annotation", Any)
    annotation = _unwrap_annotation(annotation)

    origin = get_origin(annotation)
    if origin is Union:
        args = get_args(annotation)
        has_list = False
        list_item_type: Any = Any
        non_none_non_list_args: list = []
        for arg in args:
            arg_unwrapped = _unwrap_annotation(arg)
            if get_origin(arg_unwrapped) is list:
                has_list = True
                list_args = get_args(arg_unwrapped)
                list_item_type = _unwrap_annotation(list_args[0]) if list_args else Any
            elif arg is not type(None):
                non_none_non_list_args.append(arg)
        if has_list:
            accepts_scalar = len(non_none_non_list_args) > 0
            return True, accepts_scalar, list_item_type
        non_none_args = [arg for arg in args if arg is not type(None)]
        if len(non_none_args) == 1:
            annotation = _unwrap_annotation(non_none_args[0])
            origin = get_origin(annotation)

    if origin is list:
        item_type = _unwrap_annotation(get_args(annotation)[0])
        return True, False, item_type

    if isinstance(annotation, type) and issubclass(annotation, LangStringList):
        return True, False, LangString

    return False, False, annotation


# --- FieldInfo stand-in: only `.annotation`/`.metadata`, as real Pydantic
# FieldInfo objects expose (see _get_rdf_property/_field_type_info above) ---

def FieldInfo(annotation, metadata=()):
    return SimpleNamespace(annotation=annotation, metadata=tuple(metadata))


# --- RdfBaseModelStub: `_bind_prefixes`/`_value_to_node` copied verbatim,
# `_subject_uri` simplified (see header) ------------------------------------

class RdfBaseModelStub:
    rdf_type: str | URIRef | None = None
    rdf_prefixes: dict = {}

    def __init__(self, subject_uri, **fields):
        self._fixed_subject = subject_uri
        for name, value in fields.items():
            setattr(self, name, value)

    def __eq__(self, other):
        # Structural equality, not the real class's identity-based default:
        # run_pair compares each side's own instance (built independently by
        # the driver's call() for that side) argument-by-argument, so without
        # this every call() reports a spurious "values differ" purely from
        # comparing two distinct Python objects (see meta.json).
        if type(self) is not type(other):
            return NotImplemented
        return vars(self) == vars(other)

    def _subject_uri(self, *, base_uri=None, rdf_uri_generator=None):
        return self._fixed_subject

    def _bind_prefixes(self, graph: Graph) -> None:
        prefixes = _default_prefixes()
        prefixes.update({key: str(value) for key, value in self.rdf_prefixes.items()})
        for prefix, namespace in prefixes.items():
            graph.bind(prefix, namespace)

    def _value_to_node(self, value, expected_type, prop, graph, base_uri, *, rdf_uri_generator=None):
        if prop.serializer is not None:
            value = prop.serializer(value)
        if isinstance(value, RdfBaseModelStub):
            return value._serialise_into_graph(graph, base_uri=base_uri, rdf_uri_generator=rdf_uri_generator)
        if isinstance(value, URIRef):
            return value
        if isinstance(value, Literal):
            return value
        if isinstance(value, Enum):
            value = value.value
        if isinstance(value, bytes):
            import base64
            encoded = base64.b64encode(value).decode("ascii")
            return Literal(encoded, datatype=XSD.base64Binary)
        if isinstance(value, LangString):
            return Literal(value.value, lang=value.lang)
        if isinstance(value, (datetime, date, time, int, float, bool, Decimal, uuid.UUID)):
            datatype = prop.datatype_uri()
            if datatype is None:
                datatype = _python_datatype(value)
            return Literal(value, datatype=datatype)
        if isinstance(value, str):
            datatype = prop.datatype_uri()
            if prop.language:
                return Literal(value, lang=prop.language)
            if datatype is not None:
                return Literal(value, datatype=datatype)
            allowed_types = (expected_type,)
            if URIRef in allowed_types and _looks_like_uri(value):
                return URIRef(value)
            return Literal(value)
        return Literal(value)

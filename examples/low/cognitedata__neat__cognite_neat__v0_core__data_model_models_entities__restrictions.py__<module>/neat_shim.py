# Context shim (see meta.json): the region imports six names from five modules
# of cognite.neat, whose package __init__ pulls in the whole cognite-client
# SDK (~1700 lines of transitive source, none of it installable here).  This
# module provides behavioural stand-ins for exactly those six names, reduced to
# the behaviour the region exercises, with the constants and formats taken from
# cognitedata/neat@4042d3e96d:
#   EntityTypes                (core/_data_model/_constants.py)
#   _XSD_TYPES, DataType       (core/_data_model/models/data_types.py)
#   _PARSE                     (.../models/entities/_constants.py)
#   ConceptEntity, ConceptualEntity  (.../models/entities/_single_value.py)
#   NeatValueError             (core/_issues/errors/_general.py)
#   remove_namespace_from_uri  (core/_utils/rdf_.py)
# It is a stand-in, not a copy; both representations import it identically
# (they are executed in the same process), so the equivalence verdict does not
# depend on it.
import re
from enum import StrEnum
from typing import Any, ClassVar

from pydantic import BaseModel, model_validator
from rdflib import Namespace, URIRef

XML_SCHEMA_NAMESPACE = Namespace("http://www.w3.org/2001/XMLSchema#")

# core/_data_model/_constants.py -- verbatim values of the members the region uses
ENTITY_PATTERN = re.compile(r"^(?P<prefix>.*?):?(?P<suffix>[^(:]*)(\((?P<content>.+)\))?$")


class EntityTypes(StrEnum):
    undefined = "undefined"
    concept = "concept"
    concept_restriction = "conceptRestriction"
    value_constraint = "valueConstraint"
    cardinality_constraint = "cardinalityConstraint"
    named_individual = "named_individual"


# .../models/entities/_constants.py -- verbatim
class _UndefinedType(BaseModel): ...


Undefined = _UndefinedType()
_PARSE = object()


# core/_issues/errors/_general.py -- reduced
class NeatError(Exception): ...


class NeatValueError(NeatError, ValueError):
    def __init__(self, raw_message: str) -> None:
        super().__init__(raw_message)
        self.raw_message = raw_message


# core/_utils/rdf_.py -- reduced to the single-URI, prefix-validation case
def remove_namespace_from_uri(URI: "URIRef | str", *, special_separator: str = "#_") -> str:
    uri = str(URI)
    if not uri.startswith("http"):
        return uri
    if special_separator in uri:
        return uri.split(special_separator)[-1]
    return re.split("[#/]", uri)[-1]


# .../models/entities/_single_value.py -- reduced to prefix:suffix entities
class ConceptualEntity(BaseModel, extra="ignore"):
    """Conceptual Entity is a concept, class or property in semantics sense."""

    type_: ClassVar[EntityTypes] = EntityTypes.undefined
    prefix: "str | _UndefinedType" = Undefined
    suffix: str

    @classmethod
    def load(cls, data: Any, **defaults: Any) -> "ConceptualEntity":
        if isinstance(data, cls):
            return data
        if defaults:
            return cls.model_validate({_PARSE: data, "defaults": defaults})
        return cls.model_validate(data)

    @model_validator(mode="before")
    def _load(cls, data: Any) -> Any:
        defaults: dict = {}
        if isinstance(data, dict) and _PARSE in data:
            defaults = data.get("defaults", {})
            data = data[_PARSE]
        if isinstance(data, dict):
            data.update(defaults)
            return data
        if not isinstance(data, str):
            raise ValueError(f"Cannot load {cls.__name__} from {data}")
        match = ENTITY_PATTERN.match(data.strip())
        if match is None:
            raise ValueError(f"Cannot load {cls.__name__} from {data}")
        parsed = {"prefix": match.group("prefix") or Undefined, "suffix": match.group("suffix")}
        for key, value in defaults.items():
            if key in ("prefix", "suffix") and parsed[key] in (None, "", Undefined):
                parsed[key] = value
        return parsed

    def __str__(self) -> str:
        if isinstance(self.prefix, _UndefinedType):
            return str(self.suffix)
        return f"{self.prefix}:{self.suffix}"

    def __hash__(self) -> int:
        return hash(str(self))


class ConceptEntity(ConceptualEntity):
    type_: ClassVar[EntityTypes] = EntityTypes.concept


# .../models/data_types.py -- reduced: name -> xsd local name, as_xml_uri_ref()
_DATATYPE_PATTERN = re.compile(r"^(?P<name>[^(:]*)(\((?P<content>.+)\))?$")


class DataType(BaseModel):
    xsd: ClassVar[str] = ""
    name: str = ""

    @classmethod
    def load(cls, data: Any) -> "DataType":
        if isinstance(data, DataType):
            return data
        match = _DATATYPE_PATTERN.match(str(data))
        if match is None:
            raise ValueError(f"Cannot load {cls.__name__} from {data}")
        name = match.group("name").casefold()
        if name not in _DATA_TYPE_BY_NAME:
            raise ValueError(f"Unknown data type: {data}")
        return _DATA_TYPE_BY_NAME[name]()

    @classmethod
    def as_xml_uri_ref(cls) -> URIRef:
        return XML_SCHEMA_NAMESPACE[cls.xsd]

    def __str__(self) -> str:
        return type(self).xsd

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, type(self)) and str(self) == str(other)

    def __hash__(self) -> int:
        return hash(str(self))


# (name, xsd local name) pairs of data_types.py's DataType subclasses
_DATA_TYPE_NAMES = [
    ("boolean", "boolean"), ("float", "float"), ("double", "double"),
    ("decimal", "decimal"), ("integer", "integer"),
    ("nonPositiveInteger", "nonPositiveInteger"),
    ("nonNegativeInteger", "nonNegativeInteger"),
    ("negativeInteger", "negativeInteger"), ("long", "long"),
    ("string", "string"), ("anyURI", "anyURI"),
    ("normalizedString", "normalizedString"), ("token", "string"),
    ("dateTime", "dateTime"), ("dateTimeStamp", "dateTimeStamp"),
    ("date", "date"), ("plainLiteral", "plainLiteral"), ("json", "json"),
]
_DATA_TYPE_BY_NAME = {
    name.casefold(): type(name, (DataType,), {"__annotations__": {"xsd": ClassVar[str]}, "xsd": xsd})
    for name, xsd in _DATA_TYPE_NAMES
}
_XSD_TYPES = {cls_.xsd for cls_ in _DATA_TYPE_BY_NAME.values()}

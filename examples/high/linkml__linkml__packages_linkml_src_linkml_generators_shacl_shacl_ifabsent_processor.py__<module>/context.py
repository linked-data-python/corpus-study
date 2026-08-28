# Context shim (see meta.json): the linkml / linkml_runtime bindings the
# extracted module needs, so it can execute without installing linkml.
# Provenance: linkml/linkml@680595df54.  ShaclDataType is verbatim from
# packages/linkml/src/linkml/generators/shacl/shacl_data_type.py; the
# IfAbsentProcessor base keeps the class constants and the constructor the
# region actually reaches.  Used IDENTICALLY by original.py and
# translated.ldpy.
from enum import Enum

from rdflib import URIRef


# --- linkml/generators/shacl/shacl_data_type.py (verbatim) ------------------


class DataType:
    linkml_type: str
    uri_ref: URIRef


class ShaclDataType(DataType, Enum):
    STRING = ("string", URIRef("http://www.w3.org/2001/XMLSchema#string"))
    BOOLEAN = ("boolean", URIRef("http://www.w3.org/2001/XMLSchema#boolean"))
    DURATION = ("duration", URIRef("http://www.w3.org/2001/XMLSchema#duration"))
    DATETIME = ("datetime", URIRef("http://www.w3.org/2001/XMLSchema#dateTime"))
    DATE = ("date", URIRef("http://www.w3.org/2001/XMLSchema#date"))
    TIME = ("time", URIRef("http://www.w3.org/2001/XMLSchema#time"))
    DECIMAL = ("decimal", URIRef("http://www.w3.org/2001/XMLSchema#decimal"))
    INTEGER = ("integer", URIRef("http://www.w3.org/2001/XMLSchema#integer"))
    FLOAT = ("float", URIRef("http://www.w3.org/2001/XMLSchema#float"))
    DOUBLE = ("double", URIRef("http://www.w3.org/2001/XMLSchema#double"))
    URI = ("uri", URIRef("http://www.w3.org/2001/XMLSchema#anyURI"))
    CURIE = ("curi", URIRef("http://www.w3.org/2001/XMLSchema#string"))
    NCNAME = ("ncname", URIRef("http://www.w3.org/2001/XMLSchema#string"))
    OBJECT_IDENTIFIER = ("objectidentifier", URIRef("http://www.w3.org/ns/shex#iri"))
    NODE_IDENTIFIER = ("nodeidentifier", URIRef("http://www.w3.org/ns/shex#nonLiteral"))
    JSON_POINTER = ("jsonpointer", URIRef("http://www.w3.org/2001/XMLSchema#string"))
    JSON_PATH = ("jsonpath", URIRef("http://www.w3.org/2001/XMLSchema#string"))
    SPARQL_PATH = ("sparqlpath", URIRef("http://www.w3.org/2001/XMLSchema#string"))

    def __new__(cls, linkml_type, uri_ref):
        obj = object.__new__(cls)
        obj.linkml_type = linkml_type
        obj.uri_ref = uri_ref

        return obj

    def __init__(self, linkml_type, uri_ref):
        self.linkml_type = linkml_type
        self.uri_ref = uri_ref


# --- linkml/generators/common/ifabsent_processor.py (trimmed) ---------------
# Only the parts the region touches: the special-case tuples and the
# constructor.  The abstract mapping API is supplied by the region itself.


class IfAbsentProcessor:
    """
    Processes value of ifabsent slot.

    See `<https://w3id.org/linkml/ifabsent>`_.
    """

    URI_SPECIAL_CASES = ("class_uri", "slot_uri")
    CURIE_SPECIAL_CASES = ("class_curie", "slot_curie")
    DEFAULT_RANGE_SPECIAL_CASE = "default_range"
    UNIMPLEMENTED_DEFAULT_VALUES = ("bnode", "default_ns")

    def __init__(self, schema_view):
        self.schema_view = schema_view


# --- linkml_runtime.linkml_model (annotation-only stand-ins) ----------------


class ClassDefinition:
    def __init__(self, name):
        self.name = name


class SlotDefinition:
    def __init__(self, name):
        self.name = name


EnumDefinitionName = str


# --- demo fixtures ----------------------------------------------------------
# Used by the demo harness at the end of original.py / translated.ldpy.

EXD = "https://example.org/demo#"


class _DemoSchema:
    default_range = "string"


class DemoSchemaView:
    """Minimal stand-in for linkml_runtime.SchemaView."""

    schema = _DemoSchema()

    def expand_curie(self, curie: str) -> str:
        prefix, _, local = curie.partition(":")
        return EXD + local if prefix == "ex" else curie

    def get_uri(self, element, expand: bool = False) -> str:
        curie = "ex:" + str(element.name)
        return self.expand_curie(curie) if expand else curie


demo_class = ClassDefinition("MyClass")
demo_slot = SlotDefinition("my_slot")

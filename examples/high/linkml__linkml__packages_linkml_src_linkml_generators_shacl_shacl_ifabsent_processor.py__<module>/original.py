# Extracted from linkml/linkml@680595df54 : packages/linkml/src/linkml/generators/shacl/shacl_ifabsent_processor.py
# region: <module> (lines 1-119, band high)
# licence of the source repository: see meta.json
from rdflib import Literal, URIRef

# context shim (see meta.json): linkml is not installed here; the base
# processor, the ShaclDataType enum and the model stand-ins live in a local
# module -- identical for both representations.
from context import IfAbsentProcessor
from context import ShaclDataType
from context import ClassDefinition, EnumDefinitionName, SlotDefinition


class ShaclIfAbsentProcessor(IfAbsentProcessor):
    def map_custom_default_values(self, default_value: str, slot: SlotDefinition, cls: ClassDefinition) -> (bool, str):
        return False, None

    def map_enum_default_value(
        self, enum_name: EnumDefinitionName, permissible_value_name: str, slot: SlotDefinition, cls: ClassDefinition
    ):
        return Literal(permissible_value_name)

    def map_string_default_value(self, default_value: str, slot: SlotDefinition, cls: ClassDefinition):
        return Literal(default_value, datatype=ShaclDataType.STRING.uri_ref)

    def map_integer_default_value(self, default_value: str, slot: SlotDefinition, cls: ClassDefinition):
        return Literal(default_value, datatype=ShaclDataType.INTEGER.uri_ref)

    def map_boolean_true_default_value(self, slot: SlotDefinition, cls: ClassDefinition):
        return Literal(True, datatype=ShaclDataType.BOOLEAN.uri_ref)

    def map_boolean_false_default_value(self, slot: SlotDefinition, cls: ClassDefinition):
        return Literal(False, datatype=ShaclDataType.BOOLEAN.uri_ref)

    def map_float_default_value(self, default_value: str, slot: SlotDefinition, cls: ClassDefinition):
        return Literal(default_value, datatype=ShaclDataType.FLOAT.uri_ref)

    def map_double_default_value(self, default_value: str, slot: SlotDefinition, cls: ClassDefinition):
        return Literal(default_value, datatype=ShaclDataType.DOUBLE.uri_ref)

    def map_decimal_default_value(self, default_value: str, slot: SlotDefinition, cls: ClassDefinition):
        return Literal(default_value, datatype=ShaclDataType.DECIMAL.uri_ref)

    def map_time_default_value(self, hour: str, minutes: str, seconds: str, slot: SlotDefinition, cls: ClassDefinition):
        return Literal(f"{hour}:{minutes}:{seconds}", datatype=ShaclDataType.TIME.uri_ref)

    def map_date_default_value(self, year: str, month: str, day: str, slot: SlotDefinition, cls: ClassDefinition):
        return Literal(f"{year}-{month}-{day}", datatype=ShaclDataType.DATE.uri_ref)

    def map_datetime_default_value(
        self,
        year: str,
        month: str,
        day: str,
        hour: str,
        minutes: str,
        seconds: str,
        slot: SlotDefinition,
        cls: ClassDefinition,
    ):
        return Literal(f"{year}-{month}-{day}T{hour}:{minutes}:{seconds}", datatype=ShaclDataType.DATETIME.uri_ref)

    def map_uri_or_curie_default_value(self, default_value: str, slot: SlotDefinition, cls: ClassDefinition):
        if default_value in self.CURIE_SPECIAL_CASES:
            value = self._map_curie_special_case(default_value, slot, cls)
            return Literal(value, datatype=ShaclDataType.CURIE.uri_ref)
        elif default_value in self.URI_SPECIAL_CASES:
            value = self._map_uri_special_case(default_value, slot, cls)
            return Literal(value, datatype=ShaclDataType.URI.uri_ref)
        else:
            uri = URIRef(self.schema_view.expand_curie(default_value))
            return Literal(uri, datatype=ShaclDataType.URI.uri_ref)

    def map_curie_default_value(self, default_value: str, slot: SlotDefinition, cls: ClassDefinition):
        if default_value in self.CURIE_SPECIAL_CASES:
            default_value = self._map_curie_special_case(default_value, slot, cls)
        return Literal(default_value, datatype=ShaclDataType.CURIE.uri_ref)

    def map_uri_default_value(self, default_value: str, slot: SlotDefinition, cls: ClassDefinition):
        if default_value in self.URI_SPECIAL_CASES:
            default_value = self._map_uri_special_case(default_value, slot, cls)
        return Literal(default_value, datatype=ShaclDataType.URI.uri_ref)

    def map_nc_name_default_value(self, default_value: str, slot: SlotDefinition, cls: ClassDefinition):
        raise NotImplementedError()

    def map_object_identifier_default_value(self, default_value: str, slot: SlotDefinition, cls: ClassDefinition):
        raise NotImplementedError()

    def map_node_identifier_default_value(self, default_value: str, slot: SlotDefinition, cls: ClassDefinition):
        raise NotImplementedError()

    def map_json_pointer_default_value(self, default_value: str, slot: SlotDefinition, cls: ClassDefinition):
        raise NotImplementedError()

    def map_json_path_default_value(self, default_value: str, slot: SlotDefinition, cls: ClassDefinition):
        raise NotImplementedError()

    def map_sparql_path_default_value(self, default_value: str, slot: SlotDefinition, cls: ClassDefinition):
        raise NotImplementedError()

    def _map_uri_special_case(self, default_value: str, slot: SlotDefinition, cls: ClassDefinition) -> str:
        """Return raw (unquoted) URI values for use in RDF Literals."""
        if default_value == "class_uri":
            return str(self.schema_view.get_uri(cls, expand=True))
        elif default_value == "slot_uri":
            return str(self.schema_view.get_uri(slot, expand=True))
        raise ValueError(
            f"Default value must be one of the URI special cases: {self.URI_SPECIAL_CASES}. Got: {default_value}"
        )

    def _map_curie_special_case(self, default_value: str, slot: SlotDefinition, cls: ClassDefinition) -> str:
        """Return raw (unquoted) CURIE values for use in RDF Literals."""
        if default_value == "class_curie":
            return str(self.schema_view.get_uri(cls, expand=False))
        elif default_value == "slot_curie":
            return str(self.schema_view.get_uri(slot, expand=False))
        raise ValueError(
            f"Default value must be one of the curie special cases: {self.CURIE_SPECIAL_CASES}. Got: {default_value}"
        )

    def _map_default_range_special_case(self, default_value: str, slot: SlotDefinition, cls: ClassDefinition):
        """Return default range as a string Literal."""
        default_range = self.schema_view.schema.default_range or "string"
        return Literal(default_range, datatype=ShaclDataType.STRING.uri_ref)


# --- demo harness (added identically to both representations, see meta.json):
# instantiates the processor and collects every RDF term its mapping methods
# produce into a module-level graph, so the harness can compare them.
from rdflib import Graph, Namespace
from context import DemoSchemaView, demo_class, demo_slot

EXD = Namespace("https://example.org/demo#")
_p = ShaclIfAbsentProcessor(DemoSchemaView())
_c, _s = demo_class, demo_slot
_terms = [
    ("enum", _p.map_enum_default_value("MyEnum", "VALUE_A", _s, _c)),
    ("string", _p.map_string_default_value("hello", _s, _c)),
    ("integer", _p.map_integer_default_value("42", _s, _c)),
    ("boolean_true", _p.map_boolean_true_default_value(_s, _c)),
    ("boolean_false", _p.map_boolean_false_default_value(_s, _c)),
    ("float", _p.map_float_default_value("1.5", _s, _c)),
    ("double", _p.map_double_default_value("1.5", _s, _c)),
    ("decimal", _p.map_decimal_default_value("1.50", _s, _c)),
    ("time", _p.map_time_default_value("10", "30", "00", _s, _c)),
    ("date", _p.map_date_default_value("2024", "01", "31", _s, _c)),
    ("datetime", _p.map_datetime_default_value("2024", "01", "31", "10", "30", "00", _s, _c)),
    ("uri_or_curie_special_curie", _p.map_uri_or_curie_default_value("class_curie", _s, _c)),
    ("uri_or_curie_special_uri", _p.map_uri_or_curie_default_value("slot_uri", _s, _c)),
    ("uri_or_curie_plain", _p.map_uri_or_curie_default_value("ex:thing", _s, _c)),
    ("curie_special", _p.map_curie_default_value("slot_curie", _s, _c)),
    ("curie_plain", _p.map_curie_default_value("ex:thing", _s, _c)),
    ("uri_special", _p.map_uri_default_value("class_uri", _s, _c)),
    ("uri_plain", _p.map_uri_default_value("https://example.org/thing", _s, _c)),
    ("default_range", _p._map_default_range_special_case("default_range", _s, _c)),
]
demo_graph = Graph()
for _name, _term in _terms:
    demo_graph.add((EXD[_name], EXD.value, _term))

print("custom:", _p.map_custom_default_values("whatever", _s, _c))
try:
    _p.map_nc_name_default_value("x", _s, _c)
except NotImplementedError:
    print("nc_name: NotImplementedError")

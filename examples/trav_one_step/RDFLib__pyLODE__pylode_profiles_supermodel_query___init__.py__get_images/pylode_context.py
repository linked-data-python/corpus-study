# Context shim (see meta.json): the dataclasses and helper functions that
# `get_images` depends on but does not define itself, restored verbatim
# from RDFLib/pyLODE@0d0471fb99b201182db9d3142de13fbcaee393f2:
#   - pylode/profiles/supermodel/model.py (dataclasses imported by the
#     region's `from pylode.profiles.supermodel.model import (...)`)
#   - pylode/profiles/supermodel/query/common.py (functions imported by the
#     region's `from pylode.profiles.supermodel.query.common import (...)`)
# `pylode` is not an installed dependency of this study's venv, so the two
# dotted imports in original.py/translated.ldpy are rewritten to import from
# this single local module instead -- the two source files are merged
# because both are needed and neither is importable as a real package here.
# `Metadata` (model.py) is dropped: it is not imported by the region and
# nothing here references it. Everything else is copied unmodified,
# including fields and methods the region itself never touches (Property's
# long constraint list, etc.) -- trimming those would risk changing the
# faithfully-reproduced classes' shape for no benefit, since they are cheap
# to keep whole. Identical bindings for both representations.
from abc import ABC
from dataclasses import dataclass, field
from enum import Enum, auto
from itertools import chain
from numbers import Number
import logging

from rdflib import DCTERMS, RDFS, SDO, SKOS, Dataset, Graph, Literal, URIRef

logger = logging.getLogger(__name__)

DEFAULT_ORDER_VALUE = 999999


@dataclass
class MediaObject(ABC):
    name: str
    description: str
    encoding_format: str
    source: str
    # TODO: had role
    order: int | float

    def __post_init__(self):
        if self.name is None:
            self.name = ""
        if self.description is None:
            self.description = ""
        if self.order is None:
            self.order = DEFAULT_ORDER_VALUE


@dataclass
class ImageObject(MediaObject):
    url: str
    caption: str

    def __hash__(self) -> int:
        return hash(self.url)


@dataclass
class TextObject(MediaObject):
    text: str


class ProfileType(str, Enum):
    #: The root profile, entrypoint, lowest most specific profile in the initial document.
    ROOT = auto()
    #: The base profile, the profile that describes the resource in the highest position in the profiles hierarchy.
    BASE = auto()
    #: An intermediary profile, one that is in between the root and the base profile in the profile hierarchy.
    INTERMEDIARY = auto()


@dataclass
class Profile:
    iri: URIRef
    name: str
    type: ProfileType = ProfileType.INTERMEDIARY


@dataclass
class ProfileHierarchyItem:
    iri: URIRef
    name: str
    is_profile_of: list["ProfileHierarchyItem"] = field(default_factory=list)


@dataclass
class Resource:
    iri: URIRef
    label: str
    description: str | None = None


@dataclass
class Property:
    iri: URIRef
    name: str
    description: str
    profile: Profile
    is_property_path: bool = False
    belongs_to_class: "Class" = None
    cardinality_min: int = None
    cardinality_max: int = None
    value_type: "Class" = None
    value_class_types: list["Class"] = field(default_factory=list)
    datatype: "Class" = None
    constraints: str = ""
    # The method used to extract this property. Example, sh:path, sh:targetObjectsOf, sdo:rangeIncludes, etc.
    method: str = ""
    # The property source, example, if it's from SHACL, this contains the node shape and the property shape name, if
    # both are named nodes (IRIs).
    property_source: str = ""

    # Additional constraints
    has_value: Resource | Literal | None = None
    value_in: list[Resource | Literal] | None = None
    regex_pattern: str | None = None
    language_in: list[str] | None = None
    unique_lang: bool | None = None
    min_length: int | None = None
    max_length: int | None = None
    min_exclusive: Number | None = None
    min_inclusive: Number | None = None
    max_exclusive: Number | None = None
    max_inclusive: Number | None = None
    less_than_predicates: list[Resource] | None = None
    less_than_or_equals_predicates: list[Resource] | None = None
    equals_predicates: list[Resource] | None = None
    disjoint_predicates: list[Resource] | None = None
    default_value: Resource | Literal | None = None

    def __hash__(self):
        return hash(f"{self.iri} {self.belongs_to_class.iri} {self.profile.iri}")


@dataclass
class CodedProperty(Property):
    codelist: list[Resource] = field(default_factory=list)

    def __hash__(self):
        value = f"{self.iri} {self.belongs_to_class.iri} {self.profile.iri}"
        for code in self.codelist:
            value += f" {code.iri}"
        return hash(value)


@dataclass
class SimpleCodedProperty:
    """This is used in the vocabulary summary tables.

    This class has a simpler comparison method which only checks if a coded property is unique
    based on the IRI and the codelist values.
    """

    iri: URIRef
    name: str
    description: str | None = None
    codelist: list[Resource] = field(default_factory=list)
    classes: list["Class"] = field(default_factory=list)

    def __hash__(self):
        value = f"{self.iri}"
        for code in self.codelist:
            value += f" {code.iri}"
        return hash(value)


@dataclass
class Note:
    value: str
    type: str

    def __post_init__(self):
        note_types = (
            "note",
            "Change Note",
            "Editorial Note",
            "History Note",
            "Scope Note",
        )
        if self.type not in note_types:
            raise ValueError(
                f"An instance of Note's 'type' attribute must have one of the following values: {note_types}. Received '{self.type}' instead."
            )


@dataclass
class Ontology:
    iri: str
    name: str


@dataclass
class Class:
    iri: URIRef
    name: str
    description: str = None
    subclasses: list["Class"] = field(default_factory=list)
    superclasses: list["Class"] = field(default_factory=list)
    equivalent_classes: list["Class"] = field(default_factory=list)
    properties: dict[str, list[Property]] = field(default_factory=dict)
    examples: list[MediaObject] = field(default_factory=list)
    notes: list[Note] = field(default_factory=list)
    is_defined_by: "Ontology" = None
    images: list[Literal] = field(default_factory=list)

    def __eq__(self, other):
        if not isinstance(other, Class):
            return False

        return self.iri == other.iri


@dataclass
class RDFProperty:
    iri: URIRef
    name: str
    description: str = None
    notes: list[Note] = field(default_factory=list)
    is_defined_by: "Ontology" = None
    super_properties: list["RDFProperty"] = field(default_factory=list)
    domain_includes: list[Class] = field(default_factory=list)
    range_includes: list[Class] = field(default_factory=list)
    images: list[Literal] = field(default_factory=list)


@dataclass
class ComponentModel:
    iri: URIRef
    name: str
    coded_properties: dict[str, list[CodedProperty]]
    description: str = None
    classes: list[Class] = field(default_factory=list)
    top_level_classes: list[Class] = field(default_factory=list)
    examples: list[MediaObject] = field(default_factory=list)
    order: int = None
    ignored_classes: list[URIRef] = field(default_factory=list)
    annotation_properties: list[RDFProperty] = field(default_factory=list)
    datatype_properties: list[RDFProperty] = field(default_factory=list)
    object_properties: list[RDFProperty] = field(default_factory=list)
    ontology_properties: list[RDFProperty] = field(default_factory=list)

    def __post_init__(self):
        if self.order is None:
            self.order = DEFAULT_ORDER_VALUE


def get_values(
    iri: URIRef, graph: Graph, properties: list[URIRef]
) -> list[URIRef | Literal]:
    result = list(
        chain.from_iterable([graph.objects(iri, prop) for prop in properties])
    )

    for value in result:
        if not isinstance(value, (URIRef, Literal)):
            raise ValueError(
                f"Expected only IRIs or literals but found type {type(value)} with value {value} for IRI {iri}"
            )

    return result


def get_name(iri: URIRef, graph: Graph, db: Dataset = None) -> str:
    """Get name for resource.

    If no name found for graph (profile context), look in
    dataset (union of all graphs). If still no name found,
    fall back to using a curie.
    """
    name_predicates = [RDFS.label, SKOS.prefLabel, SDO.name]

    names = get_values(iri, graph, name_predicates)

    if not names and db is not None:
        names = get_values(iri, db, name_predicates)

    if not names:
        try:
            names.append(graph.qname(iri))
        except ValueError as err:
            logger.warning(
                f"Failed to create a qname for IRI {iri}. Reason: {err}. Adding full IRI as name instead."
            )

    return str(names[0]) if len(names) > 0 else str(iri)


def get_descriptions(iri: URIRef, graph: Graph) -> str:
    descriptions = get_values(
        iri, graph, [SKOS.definition, DCTERMS.description, SDO.description]
    )
    return (
        " ".join(sorted(str(i) for i in descriptions))
        if len(descriptions) > 0
        else None
    )


def get_class(
    iri: URIRef, graph: Graph, db: Dataset, ignored_classes: list[URIRef]
) -> Class:
    name = get_name(iri, graph, db)
    subclasses = get_subclasses(iri, graph, db, ignored_classes)
    return Class(iri, name, subclasses=subclasses)


def get_subclasses(
    iri: URIRef, graph: Graph, db: Dataset, ignored_classes: list[URIRef]
) -> list[Class]:
    subclasses = filter(
        lambda x: x not in ignored_classes and isinstance(x, URIRef),
        list(graph.subjects(RDFS.subClassOf, iri)),
    )
    return sorted(
        [get_class(subclass, graph, db, ignored_classes) for subclass in subclasses],
        key=lambda x: x.name,
    )


def get_is_defined_by(iri: URIRef, graph: Graph, db: Dataset) -> Ontology | None:
    is_defined_by = get_values(iri, graph, [RDFS.isDefinedBy])
    ontology = is_defined_by[0] if len(is_defined_by) > 0 else None
    if ontology is not None:
        name = get_name(ontology, graph, db)
        return Ontology(iri=ontology, name=name)
    return None

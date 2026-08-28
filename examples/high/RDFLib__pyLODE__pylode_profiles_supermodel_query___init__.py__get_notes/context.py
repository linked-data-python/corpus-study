# Context shim (see meta.json): the pyLODE model dataclasses and query
# helpers the extracted region needs, so it can execute without installing
# pyLODE.  Copied from RDFLib/pyLODE@0d0471fb99
# (pylode/profiles/supermodel/model.py and .../query/common.py); the helper
# functions are verbatim.  Used IDENTICALLY by original.py and
# translated.ldpy.
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from itertools import chain
from numbers import Number

from rdflib import DCTERMS, RDFS, SDO, SKOS, Dataset, Graph, Literal, URIRef

logger = logging.getLogger(__name__)


# --- pylode/profiles/supermodel/model.py ------------------------------------


class ProfileType(str, Enum):
    ROOT = auto()
    BASE = auto()
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
    method: str = ""
    property_source: str = ""
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
class Class:
    iri: URIRef
    name: str
    description: str = None
    subclasses: list["Class"] = field(default_factory=list)
    superclasses: list["Class"] = field(default_factory=list)
    equivalent_classes: list["Class"] = field(default_factory=list)
    properties: dict = field(default_factory=dict)
    examples: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    is_defined_by: "Ontology" = None
    images: list[Literal] = field(default_factory=list)

    def __eq__(self, other):
        if not isinstance(other, Class):
            return False

        return self.iri == other.iri


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


# The region imports these names but never uses them (Note, which it does use,
# is reproduced verbatim above); the classes are not reproduced here (they pull
# in the rest of the pyLODE model).
class MediaObject:  # abstract base of ImageObject / TextObject
    pass


class ImageObject(MediaObject):
    pass


class TextObject(MediaObject):
    pass


class RDFProperty:
    pass


class CodedProperty(Property):
    pass


class SimpleCodedProperty:
    pass


class ComponentModel:
    pass


# --- pylode/profiles/supermodel/query/common.py (verbatim) ------------------


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

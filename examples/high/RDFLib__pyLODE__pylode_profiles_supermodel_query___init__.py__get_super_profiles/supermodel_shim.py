# Context shim (see meta.json): the region lives in
# pylode/profiles/supermodel/query/__init__.py of RDFLib/pyLODE@0d0471fb99.
# `import pylode` cannot be used here: pylode/__init__.py pulls in the HTML
# profiles, which need `dominate`, absent from the evaluation environment.
# This module therefore carries verbatim copies of exactly the bindings the
# region needs, from the same commit:
#   * ProfileHierarchyItem, Class  -- pylode/profiles/supermodel/model.py
#   * get_values, get_name         -- pylode/profiles/supermodel/query/common.py
#   * LODE                         -- pylode/profiles/supermodel/namespace.py
# Imported identically by original.py and translated.ldpy.
import logging
from dataclasses import dataclass, field
from itertools import chain

from rdflib import DCTERMS, RDFS, SDO, SKOS, Dataset, Graph, Literal, URIRef
from rdflib.namespace import DefinedNamespace, Namespace

logger = logging.getLogger(__name__)


# --- pylode/profiles/supermodel/model.py -----------------------------------

@dataclass
class ProfileHierarchyItem:
    iri: URIRef
    name: str
    is_profile_of: list["ProfileHierarchyItem"] = field(default_factory=list)


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
    is_defined_by: object = None
    images: list[Literal] = field(default_factory=list)

    def __eq__(self, other):
        if not isinstance(other, Class):
            return False

        return self.iri == other.iri


# --- pylode/profiles/supermodel/query/common.py ----------------------------

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


# --- pylode/profiles/supermodel/namespace.py -------------------------------

class LODE(DefinedNamespace):
    _fail = True
    _underscore_num = True
    _NS = Namespace("https://w3id.org/lode/ns/pylode/")

    #: lode:Module
    Module: URIRef

    #: lode:config
    config: URIRef

    #: lode:componentModel
    componentModel: URIRef

    #: lode:ignoreClass
    ignoreClass: URIRef

    #: lode:isQualifiedProfileOf
    isQualifiedProfileOf: URIRef

    #: lode:debug
    debug: URIRef

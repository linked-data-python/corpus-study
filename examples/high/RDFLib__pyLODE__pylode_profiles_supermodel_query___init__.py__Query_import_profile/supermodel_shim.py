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


# --- demo harness support (see meta.json) ----------------------------------
# The region is a method of Query, whose real __init__ loads and indexes a
# whole profile hierarchy (and prints, and fetches background ontologies).
# DemoQuery provides exactly what the region touches -- self.db,
# self.imported_profiles, self.add_to_graph -- with add_to_graph copied
# verbatim from the same file (lines 330-333).  The catalogue below is the
# shape import_profile expects: a qualified-profile node, an rdf:value /
# prof:hasResource path to a resource, and a prof:hasArtifact pointing at a
# local Turtle file.  ex:profile-a is itself a qualified profile of
# ex:profile-b, so the recursive call is exercised.
from pathlib import Path as _Path

_HERE = _Path(__file__).resolve().parent

ROOT_PROFILE_IRI = URIRef("https://example.org/root")

_CATALOGUE = f"""
@prefix lode:    <https://w3id.org/lode/ns/pylode/> .
@prefix prof:    <http://www.w3.org/ns/dx/prof/> .
@prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix ex:      <https://example.org/> .

ex:root      lode:isQualifiedProfileOf ex:qp1 .
ex:qp1       rdf:value ex:descriptor1 .
ex:descriptor1 prof:hasResource ex:resource1 .
ex:resource1 prof:hasArtifact "{_HERE / 'profile-a.ttl'}" .

ex:profile-a lode:isQualifiedProfileOf ex:qp2 .
ex:qp2       rdf:value ex:descriptor2 .
ex:descriptor2 prof:hasResource ex:resource2 .
ex:resource2 prof:hasArtifact "{_HERE / 'profile-b.ttl'}" ;
             dcterms:format "text/turtle" .
"""


class DemoQuery:
    """Stand-in for pylode's Query, restricted to what import_profile uses."""

    def __init__(self) -> None:
        self.db = Dataset(default_union=True)
        self.db.parse(data=_CATALOGUE, format="turtle")
        self.imported_profiles = []
        self.root_profile_iri = ROOT_PROFILE_IRI

    # verbatim from pylode/profiles/supermodel/query/__init__.py lines 330-333
    def add_to_graph(self, graph: Graph, graph_identifier: str) -> None:
        _graph = Graph(identifier=graph_identifier)
        for s, p, o in graph:
            self.db.add((s, p, o, _graph))

    def flatten(self) -> Graph:
        """Every quad of the dataset as a plain graph, for isomorphism."""
        g = Graph()
        for s, p, o, _c in self.db.quads((None, None, None, None)):
            g.add((s, p, o))
        return g

    def report(self) -> str:
        """Deterministic rendering: quads with their graph name, and the
        imported_profiles list, so named-graph placement is compared too."""
        def name(c):
            return str(getattr(c, "identifier", c))
        lines = ["imported_profiles: "
                 + ", ".join(str(i) for i in self.imported_profiles)]
        lines += sorted(
            f"  {name(c)} | {s} | {p} | {o}"
            for s, p, o, c in self.db.quads((None, None, None, None))
        )
        return "\n".join(lines)

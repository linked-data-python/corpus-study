# Context shim (see meta.json): subset of ontokit/services/ontology_extractor.py
# from CatholicOS/ontokit-api@23680a4d0453f5951716d045a4d05bd5396d22a4, so the
# extracted method executes outside the package.  Verbatim except for the
# removal of the members the region does not reach.  Identical bindings for
# both representations: only update_metadata is translated.
from dataclasses import dataclass

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DC, DCTERMS, OWL, RDF, RDFS


class OntologyParseError(Exception):
    """Exception raised when ontology parsing fails."""

    pass


class UnsupportedFormatError(Exception):
    """Exception raised when file format is not supported."""

    pass


@dataclass
class DetectedMetadataProperty:
    """Information about a detected metadata property in an ontology."""

    property_uri: URIRef
    property_curie: str  # e.g., "dc:title"
    current_value: str | None
    language: str | None = None


class OntologyMetadataUpdater:
    """Service for updating metadata properties in ontology files."""

    # Priority order for title properties (first found wins)
    TITLE_PROPERTIES: list[tuple[URIRef, str]] = [
        (DC.title, "dc:title"),
        (DCTERMS.title, "dcterms:title"),
        (RDFS.label, "rdfs:label"),
    ]

    # Priority order for description properties (first found wins)
    DESCRIPTION_PROPERTIES: list[tuple[URIRef, str]] = [
        (DC.description, "dc:description"),
        (DCTERMS.description, "dcterms:description"),
        (RDFS.comment, "rdfs:comment"),
    ]

    # Map file extensions to RDFLib format strings (same as extractor)
    FORMAT_MAP: dict[str, str] = {
        ".owl": "xml",
        ".rdf": "xml",
        ".ttl": "turtle",
        ".n3": "n3",
        ".jsonld": "json-ld",
    }

    def detect_title_property(
        self, graph: Graph, ontology_iri: URIRef | None
    ) -> DetectedMetadataProperty | None:
        """Detect which property is used for the ontology title."""
        if ontology_iri is None:
            return None

        for prop_uri, prop_curie in self.TITLE_PROPERTIES:
            for obj in graph.objects(ontology_iri, prop_uri):
                value = str(obj)
                language = None
                if isinstance(obj, Literal) and obj.language:
                    language = obj.language
                return DetectedMetadataProperty(
                    property_uri=prop_uri,
                    property_curie=prop_curie,
                    current_value=value,
                    language=language,
                )

        return None

    def detect_description_property(
        self, graph: Graph, ontology_iri: URIRef | None
    ) -> DetectedMetadataProperty | None:
        """Detect which property is used for the ontology description."""
        if ontology_iri is None:
            return None

        for prop_uri, prop_curie in self.DESCRIPTION_PROPERTIES:
            for obj in graph.objects(ontology_iri, prop_uri):
                value = str(obj)
                language = None
                if isinstance(obj, Literal) and obj.language:
                    language = obj.language
                return DetectedMetadataProperty(
                    property_uri=prop_uri,
                    property_curie=prop_curie,
                    current_value=value,
                    language=language,
                )

        return None

    def _find_ontology_iri(self, graph: Graph) -> URIRef | None:
        """Find the ontology IRI (subject of rdf:type owl:Ontology)."""
        for subject in graph.subjects(RDF.type, OWL.Ontology):
            if isinstance(subject, URIRef):
                return subject
        return None

    def _ensure_dc_prefix(self, graph: Graph) -> None:
        """Ensure the dc: prefix is bound in the graph."""
        dc_namespace = Namespace("http://purl.org/dc/elements/1.1/")
        # Check if dc is already bound
        existing_namespaces = dict(graph.namespaces())
        if "dc" not in existing_namespaces:
            graph.bind("dc", dc_namespace)

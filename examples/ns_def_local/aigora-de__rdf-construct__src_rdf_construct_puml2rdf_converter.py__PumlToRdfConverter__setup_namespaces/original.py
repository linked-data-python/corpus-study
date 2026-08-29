# Extracted from aigora-de/rdf-construct@670e400ea4 : src/rdf_construct/puml2rdf/converter.py
# region: PumlToRdfConverter._setup_namespaces (lines 157-189, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, Namespace, URIRef, RDF, RDFS
from rdflib.namespace import OWL, XSD
from rdf_construct.puml2rdf.model import (
    PumlAttribute,
    PumlClass,
    PumlModel,
    PumlPackage,
    PumlRelationship,
    RelationshipType,
)

def _setup_namespaces(self, packages: list[PumlPackage], classes: list[PumlClass]) -> None:
    """Set up RDF namespaces from PlantUML packages and class prefixes."""
    # Standard namespaces
    self._graph.bind("owl", OWL)
    self._graph.bind("rdfs", RDFS)
    self._graph.bind("xsd", XSD)

    # Default namespace
    default_ns = Namespace(self.config.default_namespace)
    self._namespaces[None] = default_ns  # None key for unpackaged classes
    self._graph.bind("", default_ns)

    # Collect all unique package prefixes from classes
    prefixes = {cls.package for cls in classes if cls.package}

    # Also add packages from PlantUML package declarations
    for pkg in packages:
        if pkg.namespace_uri:
            ns_uri = pkg.namespace_uri
            if not ns_uri.endswith(("#", "/")):
                ns_uri += "#"
            ns = Namespace(ns_uri)
            self._namespaces[pkg.name] = ns
            self._graph.bind(pkg.name, ns)
            prefixes.discard(pkg.name)  # Don't auto-generate

    # Auto-generate namespaces for remaining prefixes
    base = self.config.default_namespace.rstrip("#/")
    for prefix in prefixes:
        ns_uri = f"{base}/{prefix}#"
        ns = Namespace(ns_uri)
        self._namespaces[prefix] = ns
        self._graph.bind(prefix, ns)

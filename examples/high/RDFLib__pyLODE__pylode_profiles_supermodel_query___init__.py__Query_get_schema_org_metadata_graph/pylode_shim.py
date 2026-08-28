# Context shim (see meta.json): the region imports four constants from
# pylode/rdf_elements.py (RDFLib/pyLODE@0d0471fb99).  pyLODE cannot be installed
# here and its package __init__ pulls in `dominate`, so the four constants are
# reproduced verbatim below, together with the three namespaces they need that
# rdflib does not define.  Everything else in rdf_elements.py is left out.
#
# This module is imported IDENTICALLY by original.py and translated.ldpy.
from rdflib import Namespace
from rdflib.namespace import DCTERMS, OWL, RDFS, SDO, SKOS, VANN

ONTPUB = Namespace("https://linked.data.gov.au/def/ontpub/")
OBO = Namespace("http://purl.obolibrary.org/obo/")
OBOINOWL = Namespace("http://www.geneontology.org/formats/oboInOwl#")

ONTOLOGY_PROPS = [
    DCTERMS.title,
    DCTERMS.publisher,
    DCTERMS.creator,
    DCTERMS.contributor,
    DCTERMS.created,
    DCTERMS.dateAccepted,
    DCTERMS.modified,
    DCTERMS.issued,
    DCTERMS.license,
    DCTERMS.rights,
    SDO.category,
    OWL.versionIRI,
    OWL.versionInfo,
    OWL.priorVersion,
    SDO.identifier,
    VANN.preferredNamespacePrefix,
    VANN.preferredNamespaceUri,
    SKOS.historyNote,
    SKOS.scopeNote,
    DCTERMS.source,
    DCTERMS.provenance,
    SKOS.note,
    DCTERMS.description,
    ONTPUB.restriction,
    OWL.imports,
    SDO.codeRepository,
    RDFS.seeAlso,
    # SKOS.hasTopConcept, -- catered for in Concept Hierarchy
    # OBO
    OBO.IAO_0000700,
    OBOINOWL["default-namespace"],
    OBOINOWL.hasOBOFormatVersion,
]

# OWL 2 defines these property characteristic classes as
# rdfs:subClassOf owl:ObjectProperty
OBJECT_PROPERTY_SUBCLASSES = [
    OWL.SymmetricProperty,
    OWL.AsymmetricProperty,
    OWL.TransitiveProperty,
    OWL.ReflexiveProperty,
    OWL.IrreflexiveProperty,
    OWL.InverseFunctionalProperty,
]

AGENT_PROPS = [
    SDO.name,
    SDO.affiliation,
    SDO.identifier,
    SDO.email,
    SDO.honorificPrefix,
    SDO.url,
]

"""Context shim for ``pylode.rdf_elements``.

Only the four names the extracted region imports are reproduced here, copied
verbatim from RDFLib/pyLODE@0d0471fb99 ``pylode/rdf_elements.py``
(ONTPUB line 4, OBJECT_PROPERTY_SUBCLASSES lines 155-162, AGENT_PROPS lines
284-291, ONTOLOGY_PROPS lines 9-41).  ``original.py`` and ``translated.ldpy``
import this shim identically; only the extracted region differs between them.
"""

from rdflib import Namespace
from rdflib.namespace import DCTERMS, OWL, RDFS, SDO, SKOS, VANN

ONTPUB = Namespace("https://linked.data.gov.au/def/ontpub/")
OBO = Namespace("http://purl.obolibrary.org/obo/")
OBOINOWL = Namespace("http://www.geneontology.org/formats/oboInOwl#")

# OntPub
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

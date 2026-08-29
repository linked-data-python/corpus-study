# Context shim (see meta.json), for
# JonasHeinickeBio/biomedical-knowledge-lookup@00477184b3.
#
# _add_concept_mappings is a method of UnifiedRDFConverter, extracted with
# an explicit `self` parameter; two bindings it reaches through `self` are
# not in the extracted region (lines 687-717 of
# src/knowledge_lookup/services/rdf_converter.py) and are restored here,
# copied verbatim from the real source at the pinned commit:
#
#   - RDFNamespaces (lines 25-47 of that file): trimmed to the namespaces
#     `_add_concept_mappings` and `_get_concept_uri_from_identifier` (the
#     sibling method it calls, see below) actually reach -- AIDPAIS, VOCAB,
#     RDF, XSD, and the five source-specific namespaces
#     (CHEMBL/PUBCHEM/DRUGBANK/UNIPROT/ENSEMBL). Real IRIs, unchanged.
#   - UnifiedRDFConverter._get_concept_uri_from_identifier (lines 719-733 of
#     that file): a sibling method _add_concept_mappings calls on `self` to
#     resolve `mapping.to_concept`, outside the extracted region's line
#     range. Copied verbatim onto ConverterStub below.
#
# ConceptIdentifier/ConceptMapping/UnifiedConcept are minimal stand-ins for
# the pydantic models in src/knowledge_lookup/models/biomedical_knowledge_models.py
# (ConceptIdentifier lines 584-624, ConceptMapping lines 627-672, UnifiedConcept
# lines 675+), reduced to plain dataclasses carrying only the fields this
# region reads (`.mappings`, `.primary_id`, and on each mapping
# `.from_concept`/`.to_concept`/`.mapping_type`/`.confidence`/`.source`, and
# on each identifier `.source`/`.identifier`). KnowledgeSource is trimmed to
# the five members `_get_concept_uri_from_identifier` branches on. ConceptType
# is an empty placeholder: original.py imports it (as the real file does,
# for a type hint used elsewhere in rdf_converter.py) but the region never
# touches it.
#
# Identical bindings for both representations.
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from rdflib import RDF, RDFS, Namespace
from rdflib.namespace import XSD


class ConceptType:
    """Empty placeholder: imported by name only (see header above)."""


class KnowledgeSource(str, Enum):
    CHEMBL = "CHEMBL"
    PUBCHEM = "PUBCHEM"
    DRUGBANK = "DRUGBANK"
    UNIPROT = "UNIPROT"
    ENSEMBL = "ENSEMBL"
    UMLS = "UMLS"  # not resolved by any of the five branches: exercises
    # _get_concept_uri_from_identifier's `else` fallback


@dataclass
class ConceptIdentifier:
    source: "KnowledgeSource"
    identifier: str
    label: Optional[str] = None
    url: Optional[str] = None


@dataclass
class ConceptMapping:
    from_concept: ConceptIdentifier
    to_concept: ConceptIdentifier
    mapping_type: Optional[str] = None
    confidence: Optional[float] = None
    source: Optional[str] = None


@dataclass
class UnifiedConcept:
    primary_id: str
    primary_label: str = ""
    mappings: Optional[list] = None


class RDFNamespaces:
    """Centralized namespace management for AID-PAIS knowledge graph
    (trimmed verbatim copy, real IRIs -- see header)."""

    AIDPAIS = Namespace("http://www.aid-pais-kg.org/")
    VOCAB = Namespace("http://www.aid-pais-kg.org/vocab/")
    CHEMBL = Namespace("https://www.ebi.ac.uk/chembl/compound/")
    PUBCHEM = Namespace("https://pubchem.ncbi.nlm.nih.gov/compound/")
    DRUGBANK = Namespace("https://www.drugbank.ca/drugs/")
    UNIPROT = Namespace("https://www.uniprot.org/uniprotkb/")
    ENSEMBL = Namespace("https://www.ensembl.org/id/")
    RDF = RDF
    RDFS = RDFS
    XSD = XSD


class ConverterStub:
    """Stand-in for UnifiedRDFConverter: supplies `.namespaces` and the
    sibling method `_add_concept_mappings` calls on `self`."""

    def __init__(self):
        self.namespaces = RDFNamespaces()

    def _get_concept_uri_from_identifier(self, identifier):
        """Copied verbatim from UnifiedRDFConverter._get_concept_uri_from_identifier."""
        if identifier.source == KnowledgeSource.CHEMBL:
            return self.namespaces.CHEMBL[identifier.identifier]
        elif identifier.source == KnowledgeSource.PUBCHEM:
            return self.namespaces.PUBCHEM[identifier.identifier]
        elif identifier.source == KnowledgeSource.DRUGBANK:
            return self.namespaces.DRUGBANK[identifier.identifier]
        elif identifier.source == KnowledgeSource.UNIPROT:
            return self.namespaces.UNIPROT[identifier.identifier]
        elif identifier.source == KnowledgeSource.ENSEMBL:
            return self.namespaces.ENSEMBL[identifier.identifier]
        else:
            return self.namespaces.AIDPAIS[f"{str(identifier.source)}/{identifier.identifier}"]

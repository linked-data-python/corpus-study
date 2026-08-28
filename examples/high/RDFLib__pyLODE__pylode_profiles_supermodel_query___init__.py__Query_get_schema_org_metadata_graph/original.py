# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/query/__init__.py
# region: Query.get_schema_org_metadata_graph (lines 1040-1082, band high)
# licence of the source repository: see meta.json
from itertools import chain
from rdflib import Dataset, Graph, Literal, URIRef
from rdflib.namespace import (
    DC,
    DCTERMS,
    FOAF,
    ORG,
    OWL,
    PROF,
    PROV,
    QB,
    RDF,
    RDFS,
    SDO,
    SH,
    SKOS,
    VANN,
)
from pylode.rdf_elements import (
    AGENT_PROPS,
    OBJECT_PROPERTY_SUBCLASSES,
    ONTOLOGY_PROPS,
    ONTPUB,
)

def get_schema_org_metadata_graph(self):
    graph = Graph()
    for ont_iri in chain(
        self.graph.subjects(predicate=RDF.type, object=OWL.Ontology),
        self.graph.subjects(predicate=RDF.type, object=SKOS.ConceptScheme),
        self.graph.subjects(predicate=RDF.type, object=PROF.Profile),
    ):
        graph.add((ont_iri, RDF.type, SDO.DefinedTermSet))
        for p_, o in self.graph.predicate_objects(ont_iri):
            if p_ == DCTERMS.title:
                graph.add((ont_iri, SDO.name, o))
            elif p_ == DCTERMS.description:
                graph.add((ont_iri, SDO.description, o))
            elif p_ == DCTERMS.publisher:
                graph.add((ont_iri, SDO.publisher, o))
                if not isinstance(o, Literal):
                    for p2, o2 in self.graph.predicate_objects(o):
                        if p2 in AGENT_PROPS:
                            graph.add((o, p2, o2))
            elif p_ == DCTERMS.creator:
                graph.add((ont_iri, SDO.creator, o))
                if not isinstance(o, Literal):
                    for p2, o2 in self.graph.predicate_objects(o):
                        if p2 in AGENT_PROPS:
                            graph.add((o, p2, o2))
            elif p_ == DCTERMS.contributor:
                graph.add((ont_iri, SDO.contributor, o))
                if not isinstance(o, Literal):
                    for p2, o2 in self.graph.predicate_objects(o):
                        if p2 in AGENT_PROPS:
                            graph.add((o, p2, o2))
            elif p_ == DCTERMS.created:
                graph.add((ont_iri, SDO.dateCreated, o))
            elif p_ == DCTERMS.modified:
                graph.add((ont_iri, SDO.dateModified, o))
            elif p_ == DCTERMS.issued:
                graph.add((ont_iri, SDO.dateIssued, o))
            elif p_ == DCTERMS.license:
                graph.add((ont_iri, SDO.license, o))
            elif p_ == DCTERMS.rights:
                graph.add((ont_iri, SDO.copyrightNotice, o))

    return graph

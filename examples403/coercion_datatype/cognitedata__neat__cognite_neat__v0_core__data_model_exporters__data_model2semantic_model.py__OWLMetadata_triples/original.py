# Extracted from cognitedata/neat@4042d3e96d : cognite/neat/_v0/core/_data_model/exporters/_data_model2semantic_model.py
# region: OWLMetadata.triples (lines 139-160, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import DCTERMS, OWL, RDF, RDFS, XSD, BNode, Graph, Literal, Namespace, URIRef
from cognite.neat._v0.core._constants import DEFAULT_NAMESPACE as NEAT_NAMESPACE

@property
def triples(self) -> list[tuple]:
    # Mandatory triples originating from Metadata mandatory fields
    triples: list[tuple] = [
        (URIRef(self.namespace), DCTERMS.hasVersion, Literal(self.version)),
        (URIRef(self.namespace), OWL.versionInfo, Literal(self.version)),
        (URIRef(self.namespace), RDFS.label, Literal(self.name)),
        (URIRef(self.namespace), NEAT_NAMESPACE.prefix, Literal(self.prefix)),
        (URIRef(self.namespace), DCTERMS.title, Literal(self.name)),
        (URIRef(self.namespace), DCTERMS.created, Literal(self.created, datatype=XSD.dateTime)),
        (URIRef(self.namespace), DCTERMS.description, Literal(self.description)),
    ]
    if isinstance(self.creator, list):
        triples.extend([(URIRef(self.namespace), DCTERMS.creator, Literal(creator)) for creator in self.creator])
    else:
        triples.append((URIRef(self.namespace), DCTERMS.creator, Literal(self.creator)))

    # Optional triples originating from Metadata optional fields
    if self.updated:
        triples.append((URIRef(self.namespace), DCTERMS.modified, Literal(self.updated, datatype=XSD.dateTime)))

    return triples

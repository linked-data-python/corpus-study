# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/query/__init__.py
# region: Query.import_profile (lines 461-484, band high)
# licence of the source repository: see meta.json
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
from pylode.profiles.supermodel.namespace import LODE

def import_profile(self, iri: str):
    db = self.db
    qualified_profile_nodes = db.objects(
        subject=iri, predicate=LODE.isQualifiedProfileOf
    )

    for node in qualified_profile_nodes:
        resources = list(self.db.objects(node, RDF.value / PROF.hasResource))
        for resource in resources:
            graph = Graph()
            path = self.db.value(resource, PROF.hasArtifact)
            mimetype = self.db.value(resource, DCTERMS.format) or "text/turtle"
            graph.parse(path, mimetype)

            profile_iri = graph.value(
                predicate=RDF.type, object=PROF.Profile
            ) or graph.value(predicate=RDF.type, object=OWL.Ontology)

            if profile_iri is not None:
                if node not in self.imported_profiles:
                    self.imported_profiles.append(node)
                self.add_to_graph(graph, node)

                self.import_profile(profile_iri)

# Extracted from calipho-sib/nextprot-scripts@f03504ce5e : src/polish-rdf/pylode/pyLODE-2.13.2/pylode/profiles/ontdoc.py
# region: OntDoc._expand_graph (lines 246-310, stratum remove)
# licence of the source repository: see meta.json
from itertools import chain
from rdflib.namespace import DC, DCTERMS, DOAP, OWL, PROF, PROV, RDF, RDFS, SDO, SKOS

def _expand_graph(self):
    # name
    for s, o in self.G.subject_objects(DC.title | RDFS.label | SKOS.prefLabel | SDO.name):
        self.G.add((s, DCTERMS.title, o))

    # description
    for s, o in self.G.subject_objects(
            DC.description | RDFS.comment | SKOS.definition | SDO.description):
        self.G.add((s, DCTERMS.description, o))

    # property types
    for property_type in (OWL.ObjectProperty, OWL.FunctionalProperty,
                          OWL.DatatypeProperty, OWL.AnnotationProperty):
        for s in self.G.subjects(RDF.type, property_type):
            self.G.add((s, RDF.type, RDF.Property))

    # class types
    for s in self.G.subjects(RDF.type, OWL.Class):
        self.G.add((s, RDF.type, RDFS.Class))

    # owl:Restrictions from Blank Nodes
    for s in self.G.subjects(OWL.onProperty):
        self.G.add((s, RDF.type, OWL.Restriction))

    # Agents
    for target, sources in (
            # conflate SDO.author with DCTERMS.creator
            (DCTERMS.creator, (DC.creator, SDO.creator, SDO.author)),
            (DCTERMS.contributor, (DC.contributor, SDO.contributor)),
            (DCTERMS.publisher, (DC.publisher, SDO.publisher)),
    ):
        for source in sources:
            for s, o in self.G.subject_objects(source):
                for predicate in sources:
                    self.G.remove((s, predicate, o))
                self.G.add((s, target, o))

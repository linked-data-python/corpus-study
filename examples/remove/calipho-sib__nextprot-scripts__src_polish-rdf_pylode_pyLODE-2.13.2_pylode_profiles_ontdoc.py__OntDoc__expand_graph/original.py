# Extracted from calipho-sib/nextprot-scripts@f03504ce5e : src/polish-rdf/pylode/pyLODE-2.13.2/pylode/profiles/ontdoc.py
# region: OntDoc._expand_graph (lines 246-310, stratum remove)
# licence of the source repository: see meta.json
from itertools import chain
from rdflib.namespace import DC, DCTERMS, DOAP, OWL, PROF, PROV, RDF, RDFS, SDO, SKOS

def _expand_graph(self):
    # name
    for s, o in chain(
            self.G.subject_objects(DC.title),
            self.G.subject_objects(RDFS.label),
            self.G.subject_objects(SKOS.prefLabel),
            self.G.subject_objects(SDO.name)
    ):
        self.G.add((s, DCTERMS.title, o))

    # description
    for s, o in chain(
            self.G.subject_objects(DC.description),
            self.G.subject_objects(RDFS.comment),
            self.G.subject_objects(SKOS.definition),
            self.G.subject_objects(SDO.description)
    ):
        self.G.add((s, DCTERMS.description, o))

    # property types
    for s in chain(
            self.G.subjects(RDF.type, OWL.ObjectProperty),
            self.G.subjects(RDF.type, OWL.FunctionalProperty),
            self.G.subjects(RDF.type, OWL.DatatypeProperty),
            self.G.subjects(RDF.type, OWL.AnnotationProperty)
    ):
        self.G.add((s, RDF.type, RDF.Property))

    # class types
    for s in self.G.subjects(RDF.type, OWL.Class):
        self.G.add((s, RDF.type, RDFS.Class))

    # owl:Restrictions from Blank Nodes
    for s in self.G.subjects(OWL.onProperty):
        self.G.add((s, RDF.type, OWL.Restriction))

    # Agents
    # creator
    for s, o in chain(
            self.G.subject_objects(DC.creator),
            self.G.subject_objects(SDO.creator),
            self.G.subject_objects(SDO.author)  # conflate SDO.author with DCTERMS.creator
    ):
        self.G.remove((s, DC.creator, o))
        self.G.remove((s, SDO.creator, o))
        self.G.remove((s, SDO.author, o))
        self.G.add((s, DCTERMS.creator, o))

    # contributor
    for s, o in chain(
            self.G.subject_objects(DC.contributor),
            self.G.subject_objects(SDO.contributor)
    ):
        self.G.remove((s, DC.contributor, o))
        self.G.remove((s, SDO.contributor, o))
        self.G.add((s, DCTERMS.contributor, o))

    # publisher
    for s, o in chain(
            self.G.subject_objects(DC.publisher),
            self.G.subject_objects(SDO.publisher)
    ):
        self.G.remove((s, DC.publisher, o))
        self.G.remove((s, SDO.publisher, o))
        self.G.add((s, DCTERMS.publisher, o))

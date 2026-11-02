# Extracted from calipho-sib/nextprot-scripts@f03504ce5e : src/polish-rdf/pylode/pyLODE-2.13.2/pylode/profiles/prof.py
# region: Prof._expand_graph (lines 42-99, stratum remove)
# licence of the source repository: see meta.json
from rdflib.namespace import DC, DCTERMS, OWL, PROF, RDF, RDFS, SDO, SKOS
from itertools import chain

def _expand_graph(self):
    # label
    for s, o in chain(
            self.G.subject_objects(DC.title),
            self.G.subject_objects(SKOS.prefLabel),
            self.G.subject_objects(DCTERMS.title)
    ):
        self.G.remove((s, DC.title, o))
        self.G.remove((s, SKOS.prefLabel, o))
        self.G.remove((s, DCTERMS.title, o))
        self.G.add((s, RDFS.label, o))

    # comment
    for s, o in chain(
            self.G.subject_objects(DC.description),
            self.G.subject_objects(DCTERMS.description),
            self.G.subject_objects(SDO.description),
            self.G.subject_objects(SKOS.definition),
    ):
        self.G.remove((s, DC.description, o))
        self.G.remove((s, DCTERMS.description, o))
        self.G.remove((s, SDO.description, o))
        self.G.remove((s, SKOS.definition, o))
        self.G.add((s, RDFS.comment, o))

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

    # Resource Descriptors
    for s, o in self.G.subject_objects(PROF.hasResource):
        self.G.add((o, RDF.type, PROF.ResourceDescriptor))

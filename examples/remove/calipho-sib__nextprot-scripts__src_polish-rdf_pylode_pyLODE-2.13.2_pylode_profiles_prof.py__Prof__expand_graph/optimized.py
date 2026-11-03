# Extracted from calipho-sib/nextprot-scripts@f03504ce5e : src/polish-rdf/pylode/pyLODE-2.13.2/pylode/profiles/prof.py
# region: Prof._expand_graph (lines 42-99, stratum remove)
# licence of the source repository: see meta.json
from rdflib.namespace import DC, DCTERMS, OWL, PROF, RDF, RDFS, SDO, SKOS
from itertools import chain

def _expand_graph(self):
    for target, sources in (
            (RDFS.label, (DC.title, SKOS.prefLabel, DCTERMS.title)),
            (RDFS.comment, (DC.description, DCTERMS.description, SDO.description, SKOS.definition)),
            # Agents
            # conflate SDO.author with DCTERMS.creator
            (DCTERMS.creator, (DC.creator, SDO.creator, SDO.author)),
            (DCTERMS.contributor, (DC.contributor, SDO.contributor)),
            (DCTERMS.publisher, (DC.publisher, SDO.publisher)),
    ):
        for source in sources:
            for s, o in self.G.subject_objects(source):
                self.G -= [(s, p, o) for p in sources]
                self.G.add((s, target, o))

    # Resource Descriptors
    for o in self.G.objects(None, PROF.hasResource):
        self.G.add((o, RDF.type, PROF.ResourceDescriptor))

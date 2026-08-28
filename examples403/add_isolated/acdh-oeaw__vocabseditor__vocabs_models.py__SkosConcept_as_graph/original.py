# Extracted from acdh-oeaw/vocabseditor@bf418c87b3 : vocabs/models.py
# region: SkosConcept.as_graph (lines 857-886, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import DC, DCTERMS, OWL, RDF, RDFS, SKOS, XSD, Graph, Literal, URIRef
from .utils import modelprops_to_graph

def as_graph(self):
    g = Graph()
    subj = self.get_subject()
    main_concept_scheme = self.scheme.get_subject()
    g.add((subj, RDF.type, SKOS.Concept))
    g.add((subj, SKOS.prefLabel, Literal(self.pref_label, lang=self.pref_label_lang)))
    g.add((subj, SKOS.inScheme, main_concept_scheme))
    if self.notation != "":
        g.add((subj, SKOS.notation, Literal(self.notation)))
    if self.broader_concept:
        g.add((subj, SKOS.broader, URIRef(self.broader_concept.create_uri())))
    else:
        g.add((main_concept_scheme, SKOS.hasTopConcept, URIRef(subj)))
        g.add((subj, SKOS.topConceptOf, main_concept_scheme))
    for x in self.narrower_concepts.all():
        g.add((subj, SKOS.narrower, URIRef(x.create_uri())))
    for note in self.has_notes.all():
        g = g + note.as_graph()
    for source in self.has_sources.all():
        g.add((subj, DC.source, Literal(source.name, lang=source.language)))
    for label in self.has_labels.all():
        if label.label_type == "prefLabel":
            g.add((subj, SKOS.prefLabel, Literal(label.name, lang=label.language)))
        elif label.label_type == "altLabel":
            g.add((subj, SKOS.altLabel, Literal(label.name, lang=label.language)))
        elif label.label_type == "hiddenLabel":
            g.add((subj, SKOS.hiddenLabel, Literal(label.name, lang=label.language)))
        else:
            g.add((subj, SKOS.altLabel, Literal(label.name, lang=label.language)))
    return modelprops_to_graph(self, subj, g)

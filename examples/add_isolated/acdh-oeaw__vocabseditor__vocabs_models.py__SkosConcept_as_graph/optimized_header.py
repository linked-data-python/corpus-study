# Extracted from acdh-oeaw/vocabseditor@bf418c87b3 : vocabs/models.py
# region: SkosConcept.as_graph (lines 857-886, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import DC, RDF, SKOS, Graph, Literal, URIRef
from context_shim import modelprops_to_graph
from context_shim import ConceptStub, NoteStub, SkosConceptStub, SourceStub, LabelStub

def as_graph(self):
    g = Graph()
    subj = self.get_subject()
    main_concept_scheme = self.scheme.get_subject()
    g += [(subj, RDF.type, SKOS.Concept),
          (subj, SKOS.prefLabel, Literal(self.pref_label, lang=self.pref_label_lang)),
          (subj, SKOS.inScheme, main_concept_scheme)]
    if self.notation != "":
        g.add((subj, SKOS.notation, Literal(self.notation)))
    if self.broader_concept:
        g.add((subj, SKOS.broader, URIRef(self.broader_concept.create_uri())))
    else:
        g += [(main_concept_scheme, SKOS.hasTopConcept, subj),
              (subj, SKOS.topConceptOf, main_concept_scheme)]
    for x in self.narrower_concepts.all():
        g.add((subj, SKOS.narrower, URIRef(x.create_uri())))
    for note in self.has_notes.all():
        g += note.as_graph()
    for source in self.has_sources.all():
        g.add((subj, DC.source, Literal(source.name, lang=source.language)))
    label_types = ("prefLabel", "hiddenLabel")
    for label in self.has_labels.all():
        g.add((subj, SKOS[label.label_type if label.label_type in label_types else "altLabel"],
               Literal(label.name, lang=label.language)))
    return modelprops_to_graph(self, subj, g)


# Demo harness (identical on both sides, see meta.json): as_graph is a
# method body lifted out of its class, so this entry point builds a
# context_shim.SkosConceptStub -- the minimal `self` the region's own body
# reads -- and returns what as_graph(self) writes, the region's only
# RDF-observable effect (meta.oracle: isomorphism). `scenario` stays a bare
# string so the harness's per-argument comparison has something with real
# equality to compare, unlike the stub object itself.
def _note_graph(subject_uri, text):
    g = Graph()
    g.add((URIRef(subject_uri), SKOS.note, Literal(text, lang="en")))
    return g


def demo(scenario):
    if scenario == "with_broader":
        self = SkosConceptStub(
            subject_uri="http://example.org/concept/1",
            pref_label="First concept",
            pref_label_lang="en",
            scheme_uri="http://example.org/scheme/1",
            notation="N1",
            broader_concept=ConceptStub("http://example.org/concept/0"),
            narrower_concepts=[ConceptStub("http://example.org/concept/2")],
            notes=[NoteStub(_note_graph("http://example.org/concept/1", "a note"))],
            sources=[SourceStub("Some Source", "en")],
            labels=[
                LabelStub("prefLabel", "Erste", "de"),
                LabelStub("altLabel", "1st", "en"),
                LabelStub("hiddenLabel", "hidden", "en"),
                LabelStub("weird", "fallback", "en"),
            ],
        )
    else:
        self = SkosConceptStub(
            subject_uri="http://example.org/concept/9",
            pref_label="Top concept",
            pref_label_lang="en",
            scheme_uri="http://example.org/scheme/1",
            notation="",  # empty: the notation triple must NOT be added
            broader_concept=None,  # falsy: the else branch fires
            narrower_concepts=[],
            notes=[],
            sources=[],
            labels=[],
        )
    return as_graph(self)

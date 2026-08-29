# Context shim (see meta.json): stand-ins for what surrounds
# SkosConcept.as_graph in acdh-oeaw/vocabseditor@bf418c87b321468e83dbe6faa57c7aaa265ebf51 :
# vocabs/models.py, so the region executes outside the Django app (no
# settings module, no database). Identical bindings for both representations.
#
# modelprops_to_graph is transcribed VERBATIM from vocabs/utils.py (local
# clone: corpus/repos/acdh-oeaw__vocabseditor/vocabs/utils.py, lines 85-108).
# It is untouched by the translation -- as_graph's last line calls it as-is
# on both sides -- so what it does with `self` does not bear on the
# equivalence proof, as long as it runs without crashing. The stub's
# `self._meta.fields = []` makes it a genuine no-op here: a real Django
# concept instance would additionally emit dc:creator / dct:created / ...
# triples tagged via the `set_extra` field monkeypatch (models.py lines
# 787-816), left out deliberately -- reproducing Django's field-descriptor
# machinery to exercise code the translation never touches would add risk,
# not coverage, to this pair.
from rdflib import Literal, URIRef


def modelprops_to_graph(obj, subj, g):
    for field in obj._meta.fields:
        if hasattr(field, "extra") and "predicate" in field.extra:
            value = getattr(obj, field.name)
            if value:
                predicate = field.extra["predicate"]
                if "splitter" in field.extra:
                    splitter = field.extra["splitter"]
                    for item in value.split(splitter):
                        item = item.strip()
                        if item:
                            if field.extra.get("as_uri"):
                                g.add((subj, predicate, URIRef(item)))
                            else:
                                try:
                                    g.add((subj, predicate, Literal(item, datatype=field.extra["datatype"])))
                                except KeyError:
                                    g.add((subj, predicate, Literal(item)))
                else:
                    try:
                        g.add((subj, predicate, Literal(value, datatype=field.extra["datatype"])))
                    except KeyError:
                        g.add((subj, predicate, Literal(value)))
    return g


class _Meta:
    def __init__(self, fields=()):
        self.fields = list(fields)


class RelatedManager(list):
    """Stand-in for a Django related manager: `.all()` returns the rows,
    exactly as `self.narrower_concepts.all()` / `self.has_notes.all()` /
    `self.has_sources.all()` / `self.has_labels.all()` expect."""

    def all(self):
        return self


class ConceptStub:
    """Stand-in for a related SkosConcept (broader/narrower): only
    create_uri() is dereferenced by this region."""

    def __init__(self, uri):
        self._uri = uri

    def create_uri(self):
        return self._uri


class SchemeStub:
    """Stand-in for SkosConceptScheme: only get_subject() is dereferenced."""

    def __init__(self, uri):
        self._uri = URIRef(uri)

    def get_subject(self):
        return self._uri


class NoteStub:
    """Stand-in for ConceptNote: only as_graph() is dereferenced. The region
    unions its result into the running graph (`g = g + note.as_graph()`) --
    a whole other Graph, not a single triple -- so that line stays plain
    Python on both sides; no island writes a whole graph at once."""

    def __init__(self, graph):
        self._graph = graph

    def as_graph(self):
        return self._graph


class SourceStub:
    def __init__(self, name, language):
        self.name = name
        self.language = language


class LabelStub:
    def __init__(self, label_type, name, language):
        self.label_type = label_type
        self.name = name
        self.language = language


class SkosConceptStub:
    """Only the attributes/methods SkosConcept.as_graph's own body reads on
    `self` -- everything else (save(), URL helpers, MPTT/Django plumbing) is
    outside this region."""

    def __init__(self, subject_uri, pref_label, pref_label_lang, scheme_uri,
                 notation="", broader_concept=None, narrower_concepts=(),
                 notes=(), sources=(), labels=()):
        self._subject_uri = URIRef(subject_uri)
        self.pref_label = pref_label
        self.pref_label_lang = pref_label_lang
        self.scheme = SchemeStub(scheme_uri)
        self.notation = notation
        self.broader_concept = broader_concept
        self.narrower_concepts = RelatedManager(narrower_concepts)
        self.has_notes = RelatedManager(notes)
        self.has_sources = RelatedManager(sources)
        self.has_labels = RelatedManager(labels)
        self._meta = _Meta(fields=[])

    def get_subject(self):
        return self._subject_uri

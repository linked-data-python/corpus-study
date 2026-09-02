# Extracted from acdh-oeaw/acdh-django-vocabs@60355474bb : vocabs/rdf_utils.py
# region: graph_construct_qs (lines 153-170, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, Namespace, RDF, URIRef, XSD
from rdflib.namespace import DC, RDFS, SKOS
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")


def graph_construct_qs_notes(obj, concept: URIRef, g: Graph) -> None:
    """Context: restores the `obj`, `concept`, `g` bindings that
    `graph_construct_qs`'s enclosing `for obj in results:` loop provides in
    the source file (see meta.json)."""
    if obj.has_notes.all():
        for note in obj.has_notes.all():
            if note.note_type == 'note':
                g.add((concept, SKOS.note, Literal(note.name, lang=note.language)))
            elif note.note_type == 'scopeNote':
                g.add((concept, SKOS.scopeNote, Literal(note.name, lang=note.language)))
            elif note.note_type == 'changeNote':
                g.add((concept, SKOS.changeNote, Literal(note.name, lang=note.language)))
            elif note.note_type == 'editorialNote':
                g.add((concept, SKOS.editorialNote, Literal(note.name, lang=note.language)))
            elif note.note_type == 'historyNote':
                g.add((concept, SKOS.historyNote, Literal(note.name, lang=note.language)))
            elif note.note_type == 'definition':
                g.add((concept, SKOS.definition, Literal(note.name, lang=note.language)))
            elif note.note_type == 'example':
                g.add((concept, SKOS.example, Literal(note.name, lang=note.language)))
            else:
                g.add((concept, SKOS.note, Literal(note.name, lang=note.language)))

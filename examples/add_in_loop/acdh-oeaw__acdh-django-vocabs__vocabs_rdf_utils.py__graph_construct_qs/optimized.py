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
    note_types = (
        "scopeNote", "changeNote", "editorialNote", "historyNote", "definition", "example")
    for note in obj.has_notes.all():
        g.add((concept, SKOS[note.note_type if note.note_type in note_types else "note"],
               Literal(note.name, lang=note.language)))

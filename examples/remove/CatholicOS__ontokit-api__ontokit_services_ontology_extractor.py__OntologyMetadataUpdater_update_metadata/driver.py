"""Validation driver for OntologyMetadataUpdater.update_metadata.

The region is a method: it takes the ontology *as bytes*, parses it, rewrites
the title/description triples and returns the re-serialised Turtle plus a list
of change descriptions.  The oracle is therefore the returned value — and the
returned bytes are the graph, serialised, so the comparison is stricter than
isomorphism: prefix bindings and lexical forms must match too.

`self` comes from the context shim (context.py), identical for both sides:
only update_metadata itself is translated.

The five calls cover, in order:
  0. dc:title with a language tag + dcterms:description without one
     (remove-then-add, both branches of the `if …language` test);
  1. rdfs:label appearing **twice** — the point of the (s, p, None) wildcard:
     one remove must take both triples away;
  2. an ontology with no title and no description property at all
     (the `else` branches: _ensure_dc_prefix + add dc:title / dc:description);
  3. new_title/new_description left None — nothing is removed or added;
  4. the same document as an RDF/XML .rdf file, to exercise FORMAT_MAP and a
     graph whose namespace bindings come from another parser.
"""
from rdfeval.harness import run_pair

from context import OntologyMetadataUpdater

TTL_WITH_LANG = b"""@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<http://example.org/onto> a owl:Ontology ;
    dc:title "Ancien titre"@fr ;
    dcterms:description "An old description" ;
    rdfs:comment "a comment that must survive: description won on dcterms" ;
    owl:versionInfo "1.0" .

<http://example.org/onto/Thing> a owl:Class ;
    dc:title "not the ontology - must survive" ;
    rdfs:label "Thing" .
"""

TTL_TWO_LABELS = b"""@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<http://example.org/onto> a owl:Ontology ;
    rdfs:label "Titre"@fr, "Title"@en ;
    rdfs:comment "Une description"@fr, "A description"@en .
"""

TTL_BARE = b"""@prefix owl: <http://www.w3.org/2002/07/owl#> .

<http://example.org/onto> a owl:Ontology ;
    owl:versionInfo "0.1" .

<http://example.org/onto/Thing> a owl:Class .
"""

RDF_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:owl="http://www.w3.org/2002/07/owl#"
         xmlns:dcterms="http://purl.org/dc/terms/">
  <owl:Ontology rdf:about="http://example.org/onto">
    <dcterms:title xml:lang="de">Alter Titel</dcterms:title>
  </owl:Ontology>
</rdf:RDF>
"""


# One shared, stateless receiver: the driver compares the call arguments too,
# and two distinct instances of a class without __eq__ would never compare
# equal.  update_metadata never mutates `self`.
UPDATER = OntologyMetadataUpdater()


def _call(content, filename, title, description):
    def make():
        return ((UPDATER, content, filename), {
            "new_title": title, "new_description": description})
    return make


VERDICT = run_pair(
    __file__,
    entry="update_metadata",
    calls=[
        _call(TTL_WITH_LANG, "onto.ttl", "Nouveau titre", "A new description"),
        _call(TTL_TWO_LABELS, "onto.ttl", "One title", "One description"),
        _call(TTL_BARE, "bare.ttl", "Added title", "Added description"),
        _call(TTL_WITH_LANG, "onto.ttl", None, None),
        _call(RDF_XML, "onto.rdf", "Neuer Titel", "Eine Beschreibung"),
    ],
)

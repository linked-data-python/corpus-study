"""Validation driver for acdh-oeaw__acdh-django-vocabs__vocabs_skos_import.py__SkosImporter_parse_triples.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  Each input is parsed fresh for each side.

`parse_triples(self, g)` (see original.py for why `self` is an explicit
parameter and why the wrapper returns `concept_scheme`) only needs `self` to
have a `.language` attribute -- a plain `SimpleNamespace` stands in for the
real `SkosImporter` instance.

Calls, and what each one exercises:

0. `fixture.ttl`, language "und" (distinct from every tag used): one scheme;
   a field where both the dct: and the dc: predicate fire, fields with one
   predicate, two fields with none (""), both language_check() branches, an
   untyped neighbour carrying the same properties.
1. `fixture_export.rdf`, language "en": the repository's own test input
   (vocabs/tests/example_skos_export.rdf, copied verbatim; the repository's
   test calls SkosImporter on it with file_format="xml", language="en").
   RDF/XML, several values per predicate (creator, contributor, subject,
   language, description in en and de, titles in de and en), so the ";"
   joins and the description list depend on the read order of each side.
2. no skos:ConceptScheme at all: the guard's `raise` branch. The harness
   compares the two raises (type and message). Neighbours of the guard
   pattern share two of its three terms: a node typed skos:Concept, a node
   linked to skos:ConceptScheme by another predicate, skos:ConceptScheme as
   a subject typed rdfs:Class. A guard widened on any term, or replaced by
   True, returns {} instead of raising.
3. two schemes: the loop overwrites concept_scheme, and "license" is only
   written when a dct:license exists, so the result mixes both schemes in
   the order the loop visits them; one scheme also has two dct:license
   values (the last read wins).
4. a creator that is an IRI beside a literal one (the join takes the IRI as
   a string), a typed literal description (no language: falls back to
   self.language), a title found only under skos:prefLabel.
5. a dc:source that is an IRI: `s.language` raises AttributeError, on both
   sides alike (compared as a raise).
"""
from pathlib import Path
from types import SimpleNamespace

from rdflib import Graph

from rdfeval.harness import run_pair, fixture_graph

_DIR = Path(__file__).resolve().parent
FIXTURE = _DIR / "fixture.ttl"
_SELF = SimpleNamespace(language="und")  # distinct from every @lang tag used
                                          # in fixture.ttl (en/fr/de), so the
                                          # language-fallback branch and the
                                          # tag-echo branch are visibly
                                          # different, not coincidentally equal

_PREFIXES = """
@prefix ex: <http://example.org/> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
"""

_NO_SCHEME = _PREFIXES + """
ex:c1 a skos:Concept ; skos:inScheme ex:s1 ; dct:creator "Alice" .
ex:s1 ex:type skos:ConceptScheme ; dc:title "Not typed"@en .
skos:ConceptScheme a rdfs:Class .
"""

_TWO_SCHEMES = _PREFIXES + """
ex:sA a skos:ConceptScheme ; dc:title "A"@en ; dct:creator "Ann" ;
    dct:license "L1", "L2" ; dc:source "Archive A" .
ex:sB a skos:ConceptScheme ; rdfs:label "B" ; dc:creator "Ben" .
"""

_IRI_CREATOR = _PREFIXES + """
ex:sC a skos:ConceptScheme ; skos:prefLabel "C"@fr ;
    dct:creator ex:someone ; dc:creator "Cid" ;
    dct:description "42"^^xsd:integer .
"""

_IRI_SOURCE = _PREFIXES + """
ex:sD a skos:ConceptScheme ; dc:source <http://example.org/archive> .
"""


def _turtle(text):
    return lambda: ((_SELF, Graph().parse(data=text, format="turtle")), {})


def _case():
    return ((_SELF, fixture_graph(FIXTURE)), {})


def _export():
    g = Graph().parse(str(_DIR / "fixture_export.rdf"), format="xml")
    return ((SimpleNamespace(language="en"), g), {})


VERDICT = run_pair(
    __file__,
    entry='parse_triples',
    fixture="fixture.ttl",
    calls=[_case, _export, _turtle(_NO_SCHEME), _turtle(_TWO_SCHEMES),
           _turtle(_IRI_CREATOR), _turtle(_IRI_SOURCE)],
)

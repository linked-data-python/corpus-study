"""Validation driver for technologiestiftung__digital-budget-network-explorer__preprocess_graph.py__main.

Establishes semantic equivalence of original.py and translated.ldpy.

The region is a module-level statement block: both modules are executed and
every graph and every shared module-level value is compared - above all the
accumulators the loop fills (`posten`, `bereiche`, `klassen`, `hauptgruppen`,
`hauptfunktionen`, `jahre`, `titel_beschreibung`), in order.  The input graph
is fixture.ttl, parsed fresh for each side by shim.build_fixture().

What fixture.ttl exercises (see its comments):

- P1..P4: every optional predicate present, the mid-loop `continue` on
  digiKlasse "0", the trailing soll <= 0 filter, and a posten with none of
  the optional predicates (the zero-solution case of every `.first()`);
- P5: the read predicates on an untyped subject;
- neighbours of the outer anchor `?s rdf:type dh:Haushaltsposten`, each
  with a positive dh:soll and a dh:bereich so that a visit would show in
  `posten` and `bereiche`: subjects typed skos:Concept and dh:Haushaltstitel
  (same predicate, other class), a subject linked to dh:Haushaltsposten by
  dcterms:type (same object, other predicate), and the vocabulary triples
  of the repository's graph (dh:Haushaltsposten typed, rdfs:domain);
- P7, shaped as a posten of the repository's digitalhaushalt.ttl: typed
  numeric literals and an xsd:gYear, predicates the region does not read
  beside those it reads (dh:sollDigitalWeit, dh:kapitel, schema:name), a
  keyword reached by schema:keywords rather than dcterms:subject, and P7
  placed after P1 so that a read whose subject is widened returns P1's value.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)

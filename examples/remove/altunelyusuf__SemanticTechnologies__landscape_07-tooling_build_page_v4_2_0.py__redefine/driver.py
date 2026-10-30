"""Validation driver for altunelyusuf__SemanticTechnologies__landscape_07-tooling_build_page_v4_2_0.py__redefine.

redefine returns nothing: its whole effect is on the module graph `g`, which
entry="redefine" would not observe (run_pair then compares the return value and
the arguments only).  The oracle is therefore module state, and both
representations carry the same demo harness -- four calls, one per annotation
plus one that passes none -- after the definition, then the calls that the
repository never makes but that the region contains, each aimed at a guard or
a -{ } that the first four leave unproven:

- scope= on sp:Page and on sp:ReferencesRegion, two subjects that already carry
  a skos:scopeNote (the first four calls only pass scope= on sp:Doc, which has
  none, so the -{ } of skos:scopeNote matched nothing);
- note="" on sp:W1 and label="", scope="" on sp:Doc, defn="" on
  sp:ReferencesRegion: falsy values, so `is not None` must not become a truth
  test (each of the four guards has such a call);
- the fixture gives each wiped triple two neighbours that share two of its
  three terms: sp:Twin has the same predicate and object on another subject,
  and sp:Page carries the same object under another predicate
  (skos:prefLabel, rdfs:comment, skos:editorialNote, skos:altLabel).

Both parse the same fixture
(04-page/semtech_page_abox_v4_1_0.ttl, see meta.json) into a fresh `g`, and the
two `g` are compared by RDF isomorphism.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)

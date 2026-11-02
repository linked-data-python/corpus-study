"""Validation driver for judaicalink__judaicalink-labs__labs_data_management_commands_legacy_generate_rujen_translation.py__transform_rdf.

`run(task, ingraph)` (appended identically to original.py and
translated.ldpy, see meta.json) sets the module globals `prop` and
`dest_lang` the way the source's configure_task() does, then calls the region
on a fresh output graph and returns it. The region reads `ingraph`, so the
fixture is parsed again for each call and each side.

What the calls make the original show -- a language-tagged literal per
solution, whose tag is the module global `dest_lang`:

  * call 0, "en-label": translates the four skos:prefLabel of the fixture;
    one has no entry in the stand-in service (stays Cyrillic: the region logs
    through `error`), one is answered like a banned client (src != "ru": the
    region logs, does not cache and renews `translator`); the skos:altLabel /
    skos:definition triples next to them must not be read;
  * call 1, "de-label": the SAME subjects, now all served from `trans_cached`
    (the source never keys it by language: the English text comes back with
    the tag `@de`), except the one that was never cached;
  * call 2, "en-abstract": the other predicate (jlo:hasAbstract), four
    solutions: two subjects already cached by the label calls (the cache is
    per subject, not per predicate: the label's translation is reused) and
    two that only have an abstract, translated for real, tag `@en`; the
    banned one is answered as above;
  * call 3, "de-abstract": the same abstracts from the cache, tag `@de`;
  * call 4, "en-label" on an EMPTY graph: zero solutions, nothing written.
"""
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"

VERDICT = run_pair(
    __file__,
    entry="run",
    calls=[
        lambda: (("en-label", fixture_graph(FIXTURE)), {}),
        lambda: (("de-label", fixture_graph(FIXTURE)), {}),
        lambda: (("en-abstract", fixture_graph(FIXTURE)), {}),
        lambda: (("de-abstract", fixture_graph(FIXTURE)), {}),
        lambda: (("en-label", Graph()), {}),
    ],
)

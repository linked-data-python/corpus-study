"""Validation driver for OpenEnergyPlatform__oeplatform__ontology_utils.py__read_oeo_context_information.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

The region does not take a graph directly: it takes `path` and `file`, joins
them, and parses the result itself (`g.parse(Ontology_URI.as_posix())`), so
the usual `fixture=` shortcut (which hands a pre-parsed Graph as the single
argument) does not fit this signature. `calls=` passes `(path, file)`
pointing at fixture.ttl instead, and reads it fresh on each side because
`g.parse` opens the file itself every call.

Two calls exercise both branches of `if ontology in [OPEN_ENERGY_ONTOLOGY_NAME]`:
one with `ontology="oeo"` (all five queries run, including the two obo:
queries), one with `ontology=None` (only the first three run, and
classes_definitions/classes_notes fall back to empty dicts).

Calls added on 2026-10-30 (repair after triage):

* `fixture_oeo.owl`, ontology="oeo": the input in the form the repository
  really reads. The only caller, get_common_data(), passes `oeo-full.owl`, an
  RDF/XML release; the original's three PREFIX-less queries resolve `dc:` and
  `obo:` from the xmlns declarations of that file, the translation from its
  @prefix lines. The fixture copies the release header (xmlns:obo, xmlns:dc,
  xml:base), so equality here shows the two resolutions agree on the real
  input. It also carries language-tagged, typed and plain literals,
  two definitions and two notes on one class (list append), dcterms
  `description` and `obo:IAO_0000117` as neighbours that must not match, a
  blank-node and an IRI superclass on one class (FILTER(!isBlank)).
* the same file with ontology="oeox" (OEO_EXT_NAME): a real ontology name
  that is not OPEN_ENERGY_ONTOLOGY_NAME, so the else branch on a graph where
  the obo: queries would have found rows.
* `fixture_none.ttl`, ontology="oeo": the zero-solution case for all five
  queries (empty dicts, ontology_description stays ""); each triple uses a
  neighbouring predicate, so a pattern widened to ?p would match.

Not exercised, on purpose: a file that does NOT declare obo:. There the
original raises "Unknown namespace prefix : obo" and the translation
answers (its @prefix is fixed at transpilation). The repository never passes
such a file (see meta.json repair.remaining).
"""
from pathlib import Path

from rdfeval.harness import run_pair

_EX_DIR = Path(__file__).resolve().parent

VERDICT = run_pair(
    __file__,
    entry='read_oeo_context_information',
    calls=[
        lambda: ((_EX_DIR, "fixture.ttl"), {"ontology": "oeo"}),
        lambda: ((_EX_DIR, "fixture.ttl"), {"ontology": None}),
        lambda: ((_EX_DIR, "fixture_oeo.owl"), {"ontology": "oeo"}),
        lambda: ((_EX_DIR, "fixture_oeo.owl"), {"ontology": "oeox"}),
        lambda: ((_EX_DIR, "fixture_none.ttl"), {"ontology": "oeo"}),
    ],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)

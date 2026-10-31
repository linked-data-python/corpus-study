"""Validation driver for mhrimaz__aasbrain-concept-description-repo__app_models_referable.py__Referable_from_rdf.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

`from_rdf` takes two arguments (graph, subject), so we build the calls
ourselves rather than relying on the single-argument `fixture=` shortcut.

The last three calls were added by the mutation audit (2026-10-31), against
`fixture_audit.ttl`, whose display-name and description nodes are blank nodes
as the repository writes them. Before them, these translation mutants stayed
green: `.first()` -> `.one()` or `next(iter(...))` on four of the six inner
reads (every node had exactly one language and one text), the inner
language read widened to `[]` or to `?p`, the description loop cut to its
first item, and every `if ref:` guard rewritten `if ref is not None:` (no
`""` literal anywhere). Each call says what it exercises:
  - ex:audit: "" category and idShort, no displayName, three descriptions
    (full / "" language and text / neither);
  - ex:audit2: three display names (no language / "" / two languages);
  - ex:neighbour: stored first, so a widened `[] lang ?o` read on the other
    subjects returns the neighbour's value.
"""
from pathlib import Path
from rdflib import URIRef
from rdfeval.harness import run_pair, fixture_graph

_HERE = Path(__file__).resolve().parent
_SUBJECT = URIRef("http://example.org/subject")
_NO_CATEGORY = URIRef("http://example.org/noCategory")
_AUDIT = URIRef("http://example.org/audit")
_AUDIT2 = URIRef("http://example.org/audit2")
_NEIGHBOUR = URIRef("http://example.org/neighbour")

VERDICT = run_pair(
    __file__,
    entry='from_rdf',
    calls=[
        lambda: ((fixture_graph(_HERE / "fixture.ttl"), _SUBJECT), {}),
        lambda: ((fixture_graph(_HERE / "fixture.ttl"), _NO_CATEGORY), {}),
        lambda: ((fixture_graph(_HERE / "fixture_audit.ttl"), _AUDIT), {}),
        lambda: ((fixture_graph(_HERE / "fixture_audit.ttl"), _AUDIT2), {}),
        lambda: ((fixture_graph(_HERE / "fixture_audit.ttl"), _NEIGHBOUR), {}),
    ],
)

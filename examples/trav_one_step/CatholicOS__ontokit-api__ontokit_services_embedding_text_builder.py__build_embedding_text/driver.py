"""Validation driver for CatholicOS__ontokit-api__ontokit_services_embedding_text_builder.py__build_embedding_text.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

build_embedding_text(graph, entity_uri, entity_type) needs more than the
graph, so `calls=` supplies (entity_uri, entity_type) explicitly -- the
default single-graph call (`fixture=` alone) does not apply here.

Three calls: (1) ex:Animal/"class" -- two labels (primary + extra), a
comment that must win over a definition, one parent filtered out
(owl:Thing) and one kept with its own label, one alt label, and a
non-literal rdfs:label object that must be dropped by the isinstance
filter; (2) ex:WorksAt/"property" -- the subPropertyOf branch and the
"no comment, fall back to definition" branch; (3) ex:Empty/"class" -- the
zero-solution case across every field in the region (falls back to
_local_name, no description, no parents, no alt labels).

Added by the 2026-10-31 mutation audit:

(4) ex:Restricted/"class" -- an owl:Restriction blank-node parent (dropped
by `isinstance(p, URIRef)`), a parent with no label (`_local_name`), a
parent whose first rdfs:label is an IRI (the parent-label read must skip
it), an rdfs:subPropertyOf the class branch must ignore, and two labels with
the same string (the extra-label filter).

The bindings check.  The repository passes the graph it parsed from the
project's own ontology file and caches (ontology.py load_from_git,
load_from_storage), then serialises it (OntologyService.serialize) and reads
its prefixes (linter.py).  An `@graph graph` in the region binds the block's
`@prefix` declarations into that graph, renaming a namespace the file had
bound under another prefix.  `fixture_prefixes.ttl` names SKOS `sk:` and
OWL `ow:`; each side runs the region on its own parse of it, and the result
and the graph's bindings after the call are compared: every binding of the
original must still be in the translation.  The check runs after `run_pair`
and is merged into its single RDFEVAL-VERDICT line, the only one
`rdfeval check` reads.
"""
import contextlib
import io
import json
import sys
from pathlib import Path

from rdflib import Namespace

from rdfeval.harness import _exec_artefact, fixture_graph, run_pair, sides_from_env

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"

EX = Namespace("http://example.org/")


def call_class_with_parents_and_alt():
    return ((fixture_graph(FIXTURE), EX.Animal, "class"), {})


def call_property_definition_fallback():
    return ((fixture_graph(FIXTURE), EX.WorksAt, "property"), {})


def call_zero_solutions():
    return ((fixture_graph(FIXTURE), EX.Empty, "class"), {})


def call_owl_parents():
    return ((fixture_graph(FIXTURE), EX.Restricted, "class"), {})


_stderr = io.StringIO()
with contextlib.redirect_stderr(_stderr):
    VERDICT = run_pair(
        __file__,
        entry='build_embedding_text',
        fixture="fixture.ttl",
        calls=[call_class_with_parents_and_alt, call_property_definition_fallback,
               call_zero_solutions, call_owl_parents],
        # ordered=True only if the region imposes an order (sorted, ORDER BY):
        # no store promises one, so results are compared as multisets.
    )


def _after_call(artefact, name):
    """Result and graph bindings after the region ran, for one side."""
    ns, _ = _exec_artefact(HERE / artefact, name)
    graph = fixture_graph(HERE / "fixture_prefixes.ttl")
    text = ns["build_embedding_text"](graph, EX.Animal, "class")
    return text, {(p, str(n)) for p, n in graph.namespaces()}


try:
    _left, _right = sides_from_env()
    (_ro, _bo), (_rt, _bt) = (_after_call(_left, "__original_bindings__"),
                              _after_call(_right, "__translated_bindings__"))
    if _ro != _rt:
        VERDICT["diffs"].append(f"bindings call: result differs ({_ro!r} vs {_rt!r})")
    if not _bo <= _bt:
        VERDICT["diffs"].append("bindings call: prefix bindings of the original "
                                f"missing from the translation: {sorted(_bo - _bt)}")
    VERDICT["bindings_compared"] = len(_bo)
except Exception as _e:                  # noqa: BLE001 - reported in the verdict
    VERDICT["diffs"].append(f"bindings check: {type(_e).__name__}: {_e}")
VERDICT["equivalent"] = not VERDICT["diffs"] and not VERDICT.get("error")

for _line in _stderr.getvalue().splitlines():
    if not _line.startswith("RDFEVAL-VERDICT "):
        print(_line, file=sys.stderr)
print("RDFEVAL-VERDICT " + json.dumps(VERDICT), file=sys.stderr)

"""Validation driver for ScaDS__KGpipe__src_kgpipe_tasks_entity_resolution_fusion_preference.py__fusion_first_value.

Module-level region (kind: statement) with no entry point: `original.py`
and `translated.ldpy` are both executed top to bottom and their module
globals compared (entry=None). Two rdflib Graphs are in scope --
`source_graph` (read-only input, identical on both sides, compared only for
completeness) and `seed_graph` (what the region mutates) -- so the oracle is
RDF isomorphism on `seed_graph` (meta.oracle == "isomorphism"). The
`current_subjects` set (plain strings) is also compared via
rdfeval.harness's module-level value comparison, as an extra check that both
sides walk source_graph identically; `selected`/`discarded` (lists of
TrackRecord, a pydantic model) fall outside what the harness can compare
(only RDF terms/primitives/their containers) so they are not part of the
verdict, but keeping them mirrors the source faithfully.

Context shim kgpipe_context.py restores TrackRecord (verbatim), the real
TARGET_ONTOLOGY_NAMESPACE value from the sibling kgpipe/common/config.py at
the same commit, identity stand-ins for canonicalize_entity_term/
canonicalize_property_term (their real bodies need an external match file
this pair has no reason to fabricate -- entity matching is not what this
region does), concrete allowed_predicates/fusable_properties sets standing
in for ones the real code builds from an external ontology file, and
build_fixture_graphs() -- a factory (not a shared Graph import: see the
shim's own header) returning a fresh (source_graph, seed_graph) pair built
to exercise every branch: a fusable predicate with no existing seed value
(added), a fusable predicate whose subject already has a seed value
(discarded), an rdf:type triple whose object sits outside
TARGET_ONTOLOGY_NAMESPACE (skipped before the fusable check even runs), a
predicate absent from allowed_predicates entirely (skipped), a non-fusable
but allowed predicate not yet in the seed graph (copied), and the same
non-fusable predicate where the EXACT triple already sits in the seed graph
(skipped -- the dedupe check, zero triples added for that one).
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry=None, calls=None)

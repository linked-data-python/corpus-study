"""Validation driver for ScaDS__KGpipe__src_kgpipe_tasks_entity_resolution_fusion_preference.py__select_first_value.

`select_first_value` reads two graphs from N-Triples FILES and writes its
result to another file, so the oracle here is not `fixture=` (which passes
ONE parsed Graph as the entry point's single argument): the region's own
signature is `select_first_value(inputs, outputs)`, both dicts of `Data`
objects wrapping file paths. `entry` is instead the `demo` harness both
files carry identically (see meta.json and the note in `original.py`): it
writes `source_nt`/`target_nt` to a fresh temp dir, points a minimal
`OntologyUtil` shim (context_shim.py) at `ontology_props`, runs the region,
and returns the graph parsed back from `outputs["output"].path` -- design
record corpus/405's "equality of the values produced from the same input
graph", just with the graph delivered and collected through files because
the region itself does.

This region carries TWO trav_existence reads:

  (1) `not any(seed_graph.objects(s_can, p_can))`, in the FUSABLE branch --
      gates whether a value is adopted for a (subject, cardinality-1
      predicate) pair AT ALL. Both directions are observable in the final
      graph: guard wrongly True adds a second value where only one should
      survive (extra triple); guard wrongly False drops the sole value
      (missing triple).
  (2) `(s_can, p_can, o_can) not in seed_graph`, in the NON-FUSABLE branch --
      guards a `.add()` of the SAME triple regardless of the guard's
      result, and `Graph.add` is idempotent (a set): when the triple is
      ALREADY present, whether the guard fires or not, the resulting graph
      is identical either way. So only ONE direction of this specific guard
      is observable through the region's own output -- "wrongly thinks an
      ABSENT triple is present" (skips an add that should happen, so the
      triple goes missing) -- never the other ("wrongly thinks a PRESENT
      triple is absent", since re-adding it changes nothing). The fixture
      below still includes an already-present case (s4) for realism, but it
      cannot discriminate a correct translation from an incorrect one on
      its own; that is a property of the region's OWN idempotent-add
      design, not a gap in this driver -- see the note in meta.json.

One call exercises every subject the region would ever see together, since
`select_first_value` processes the whole `source_graph` in one pass and
nothing here makes different subjects interact:

  s1  fusable (rdfs:label), seed ALREADY has "existing" -> "new" from
      source must NOT be added (check 1, guard-False direction)
  s2  fusable (rdfs:label), absent from seed entirely -> "firstval" MUST be
      added (check 1, guard-True direction)
  s3  non-fusable (skos:altLabel); seed has "seedAlt" for s3, source offers
      a DIFFERENT object "sourceAlt" -> "sourceAlt" MUST be added (check 2,
      the one discriminating direction; also proves the pattern matches on
      the object, not just subject+predicate: a translation that dropped
      the object would see s3+skos:altLabel already present and skip it)
  s4  non-fusable, EXACT triple already in both graphs -> no change either
      way (non-discriminating, see above)
  s5  predicate NOT in allowed_predicates at all -> skipped entirely by
      surrounding (untranslated) Python logic, never reaches either check;
      included so a translation that accidentally widened a pattern and
      started matching/copying everything would be caught too
  s6  fusable (rdfs:label), seed has s6 already but only for an UNRELATED
      predicate (skos:altLabel, not rdfs:label) -> "onlyLabel" MUST still
      be added (check 1, predicate specificity: a translation that
      matched on subject alone -- "does s6 have ANY triple at all" --
      would wrongly see s6 as already covered and discard it; s1/s2 alone
      cannot catch this since s1's only seed triple already IS the
      predicate under test and s2 has no seed triple at all, so a
      subject-only match happens to coincide with the correct answer for
      both -- confirmed by deliberately loosening the pattern to `{s_can}
      ?anyp ?o` below and seeing s1/s2 alone stay green while adding s6
      turns it red, see meta.json)

A second, empty call is the trivial zero-solution baseline: nothing in,
nothing out.
"""
from rdfeval.harness import run_pair

EX = "http://example.org/"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"
SKOS = "http://www.w3.org/2004/02/skos/core#"

TARGET_NT = (
    f'<{EX}s1> <{RDFS}label> "existing" .\n'
    f'<{EX}s3> <{SKOS}altLabel> "seedAlt" .\n'
    f'<{EX}s4> <{SKOS}altLabel> "dup" .\n'
    f'<{EX}s6> <{SKOS}altLabel> "unrelated" .\n'
)

SOURCE_NT = (
    f'<{EX}s1> <{RDFS}label> "new" .\n'
    f'<{EX}s2> <{RDFS}label> "firstval" .\n'
    f'<{EX}s3> <{SKOS}altLabel> "sourceAlt" .\n'
    f'<{EX}s4> <{SKOS}altLabel> "dup" .\n'
    f'<{EX}s5> <{EX}customPred> "ignored" .\n'
    f'<{EX}s6> <{RDFS}label> "onlyLabel" .\n'
)


def _case(source_nt, target_nt, ontology_props=()):
    def make():
        return (source_nt, target_nt, ontology_props), {}
    return make


VERDICT = run_pair(
    __file__,
    entry="demo",
    calls=[
        _case(SOURCE_NT, TARGET_NT),
        _case("", ""),  # zero-solution baseline: empty in, empty out
    ],
)
